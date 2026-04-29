import fitz  # PyMuPDF
from typing import List, Optional
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
import os
from langchain_core.prompts import ChatPromptTemplate
from tools.logger import logger
from objects import ContractObject, ClauseRisk
from datetime import date
import re

class ContractMetadata(BaseModel):
    contract_type: str = Field(description="e.g., MSA, NDA, SOW")
    effective_date: Optional[str] = Field(description="Date the contract becomes effective")
    expiration_date: Optional[str] = Field(description="Date the contract expires")
    parties: List[str] = Field(description="List of all entities involved in the contract")
    governing_law: Optional[str] = Field(description="Jurisdiction or governing law")

def extract_metadata_using_llm(text_chunk: str) -> ContractMetadata:
    """
    Extracts structured metadata from a text chunk of a contract using an LLM.
    """
    # Initialize the LLM using OpenRouter
    llm = ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        model="nvidia/nemotron-3-super-120b-a12b:free",
        temperature=0,
    )
    
    # Bind the Pydantic schema to the LLM
    structured_llm = llm.with_structured_output(ContractMetadata)
    
    # Create the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert legal assistant. Extract the requested fields from the provided contract text."),
        ("human", "{text}")
    ])
    
    # Create the chain
    chain = prompt | structured_llm
    
    # Execute extraction
    return chain.invoke({"text": text_chunk})

def extract_text(elements):
    """
    Extract text content from unstructured partition elements
    """
    text_content = []
    for element in elements:
        if hasattr(element, 'text') and element.text.strip():
            text_content.append(element.text)
    return "\n".join(text_content)

def parse_clauses(text_content):
    """
    Parse and analyze clauses from contract elements
    """
    clauses = []
    
    # Simple clause detection - look for common legal clause patterns
    clause_patterns = [
        ("liability", r"(?i)liability|limitation.*liability|indemnif\w+"),
        ("payment", r"(?i)payment|fee|cost|billing|invoice"),
        ("termination", r"(?i)terminate|termination|end.*agreement"),
        ("confidentiality", r"(?i)confidential|proprietary|trade.*secret"),
        ("governing law", r"(?i)governing.*law|jurisdiction|applicable.*law")
    ]

    for clause_type, pattern in clause_patterns:
        matches = re.findall(pattern, text_content)
        if matches:
            # Find the relevant text around the match
            for match in matches:
                # Simple risk scoring based on clause type
                risk_scores = {
                    "liability": 75,
                    "payment": 50,
                    "termination": 60,
                    "confidentiality": 40,
                    "governing law": 20
                }
                
                clause = ClauseRisk(
                    clause_type=clause_type.title(),
                    content=f"Found {clause_type} clause mentioning: {match}",
                    risk_score=risk_scores.get(clause_type, 30),
                    risk_tag="High" if risk_scores.get(clause_type, 30) > 60 else "Medium" if risk_scores.get(clause_type, 30) > 30 else "Low",
                    recommendation=f"Review {clause_type} clause carefully"
                )
                clauses.append(clause)
    
    return clauses

def extract_text_from_pdf(file_path: str):
    """
    Extract text from PDF using PyMuPDF (no Poppler required)
    """
    try:
        doc = fitz.open(file_path)
        text_content = ""
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text_content += page.get_text()
        doc.close()
        return text_content
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        raise e

def normalize_parties(parties_field):
    """
    Normalize parties field to ensure it's always a list
    """
    if isinstance(parties_field, list):
        return parties_field
    elif isinstance(parties_field, str):
        # Split by common delimiters if it's a string
        if ',' in parties_field:
            return [p.strip() for p in parties_field.split(',')]
        elif ' and ' in parties_field.lower():
            return [p.strip() for p in parties_field.replace(' and ', ',').split(',')]
        elif ' between ' in parties_field.lower():
            # Extract parties from "between Party A and Party B" format
            text = parties_field.lower()
            if ' between ' in text:
                after_between = text.split(' between ')[1]
                return [p.strip() for p in after_between.replace(' and ', ',').split(',')]
        else:
            return [parties_field.strip()]
    else:
        return ["Unknown Party"]

def ingest_contract(file_path: str):
    """
    Main contract ingestion function
    """
    try:
        # 1. Extract text content from PDF (no Poppler needed)
        text_content = extract_text_from_pdf(file_path)
        logger.info(f"Extracted {len(text_content)} characters of text from {file_path}")
        
        # Create a simple elements structure for compatibility
        elements = [{"text": text_content}]
        
        # 3. Extract metadata using LLM
        metadata = extract_metadata_using_llm(text_content)
        logger.info(f"Extracted metadata: {metadata}")
        
        # 4. Normalize parties to ensure it's a list
        parties_list = normalize_parties(metadata.parties)
        logger.info(f"Normalized parties: {parties_list}")
        
        # 5. Parse clauses
        clauses = parse_clauses(text_content)
        logger.info(f"Parsed {len(clauses)} clauses")
        
        # 6. Create contract object
        contract_data = ContractObject(
            contract_name=parties_list[0] if parties_list and len(parties_list) > 0 else "Unknown Contract",
            counterparty=parties_list[1] if parties_list and len(parties_list) > 1 else "Unknown Party",
            execution_date=metadata.effective_date,  # Use current date as placeholder
            expiry_date=metadata.expiration_date,    # Use current date as placeholder
            raw_text_s3_path=file_path,   # Store file path for now
            summary=f"{metadata.contract_type} contract between {', '.join(parties_list) if parties_list else 'Unknown parties'}",
            clauses=clauses,
            overall_risk_score=sum(clause.risk_score for clause in clauses) // len(clauses) if clauses else 0,
            legal_risk_score=sum(clause.risk_score for clause in clauses if clause.clause_type in ["Liability", "Confidentiality"]) // max(1, len([c for c in clauses if c.clause_type in ["Liability", "Confidentiality"]])),
            financial_risk_score=sum(clause.risk_score for clause in clauses if clause.clause_type == "Payment") // max(1, len([c for c in clauses if clause.clause_type == "Payment"])),
            operational_risk_score=sum(clause.risk_score for clause in clauses if clause.clause_type == "Termination") // max(1, len([c for c in clauses if clause.clause_type == "Termination"])),
            audit_log=[f"Contract ingested on {date.today()}"]
        )
        
        logger.info(f"Successfully created contract object: {contract_data.contract_name}")
        return contract_data
        
    except Exception as e:
        logger.error(f"Error ingesting contract: {str(e)}")
        raise e