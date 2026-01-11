import asyncio
import logging
import os
import json
from typing import Any, Dict, List, Tuple

import vertexai
from vertexai.generative_models import GenerativeModel, Part
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TripleValidation:
    """A class to perform a 3-step validation of a lead."""

    def __init__(self, vertex_ai_client=None):
        """Initialize the validation system."""
        if os.environ.get("GCP_SA_KEY"): 
            credentials = service_account.Credentials.from_service_account_info(json.loads(os.environ["GCP_SA_KEY"]))
            vertexai.init(project="infinity-x-one-systems", location="us-central1", credentials=credentials)
        else:
            # Fallback for local development without service account
            vertexai.init(project="infinity-x-one-systems", location="us-central1")

    async def validate(self, lead_data: Dict[str, Any]) -> Tuple[bool, float, str]:
        """Perform the full 3-step validation process.

        Args:
            lead_data: The lead data to validate.

        Returns:
            A tuple containing:
                - bool: The overall validation result.
                - float: The confidence score.
                - str: A summary of the validation process.
        """
        logging.info(f"Starting validation for lead: {lead_data.get('id')}")

        # Step 1: Initial Data Integrity Check
        step1_result, step1_confidence = await self.step1_data_integrity(lead_data)
        if not step1_result:
            return False, step1_confidence, "Step 1: Data Integrity Check Failed"

        # Step 2: Parallel External Verification
        step2_result, step2_confidence = await self.step2_parallel_verification(lead_data)
        if not step2_result:
            return False, step2_confidence, "Step 2: Parallel External Verification Failed"

        # Step 3: Intelligent Validation with Vertex AI
        step3_result, step3_confidence = await self.step3_intelligent_validation(lead_data)
        if not step3_result:
            return False, step3_confidence, "Step 3: Intelligent Validation Failed"

        overall_confidence = (step1_confidence + step2_confidence + step3_confidence) / 3
        logging.info(f"Validation successful for lead: {lead_data.get('id')} with overall confidence: {overall_confidence:.2f}")
        return True, overall_confidence, "All validation steps passed"

    async def step1_data_integrity(self, lead_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Perform initial data integrity checks."""
        logging.info("Performing Step 1: Data Integrity Check")
        required_fields = ["id", "name", "email"]
        missing_fields = [field for field in required_fields if field not in lead_data]
        if missing_fields:
            logging.error(f"Missing fields: {', '.join(missing_fields)}")
            return False, 0.0

        if not isinstance(lead_data.get("id"), str) or not isinstance(lead_data.get("name"), str) or not isinstance(lead_data.get("email"), str):
            logging.error("Invalid data types for lead fields.")
            return False, 0.1

        # Basic email format validation
        if "@" not in lead_data.get("email", "") or "." not in lead_data.get("email", "").split("@")[-1]:
            logging.error(f"Invalid email format: {lead_data.get('email')}")
            return False, 0.2

        logging.info("Data integrity check passed.")
        return True, 1.0

    async def step2_parallel_verification(self, lead_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Perform parallel external verification."""
        logging.info("Performing Step 2: Parallel External Verification")
        tasks = [
            self.verify_source_1(lead_data),
            self.verify_source_2(lead_data),
        ]
        results = await asyncio.gather(*tasks)

        successful_verifications = sum(1 for result, _ in results if result)
        if successful_verifications == 0:
            logging.error("All external verifications failed.")
            return False, 0.0

        confidence = sum(confidence for _, confidence in results) / len(results)
        logging.info(f"Parallel verification completed with {successful_verifications} successful verifications.")
        return True, confidence

    async def verify_source_1(self, lead_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Mock verification with an external source."""
        await asyncio.sleep(1)  # Simulate network latency
        # In a real implementation, this would involve an API call to an external service.
        # For this example, we'll just simulate a successful validation.
        logging.info("Source 1 verification successful.")
        return True, 0.9

    async def verify_source_2(self, lead_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Mock verification with another external source."""
        await asyncio.sleep(1.5)  # Simulate network latency
        # Simulate a failure for demonstration purposes
        logging.info("Source 2 verification successful.")
        return True, 0.95

    async def step3_intelligent_validation(self, lead_data: Dict[str, Any]) -> Tuple[bool, float]:
        """Perform intelligent validation using Vertex AI."""
        logging.info("Performing Step 3: Intelligent Validation with Vertex AI")
        try:
            model = GenerativeModel("gemini-1.0-pro")
            prompt = f"Analyze the following lead data and provide a confidence score (0.0 to 1.0) on its validity. Consider the source, the data itself, and any potential red flags. Lead data: {lead_data}"
            response = await model.generate_content_async([prompt])
            
            # Extract confidence score from the model's response
            # This is a simplified example; a more robust solution would parse the response more carefully
            confidence_score = float(response.text)
            is_valid = confidence_score >= 0.7 # Set a threshold for validity

            logging.info(f"Vertex AI validation completed with confidence: {confidence_score:.2f}")
            return is_valid, confidence_score
        except Exception as e:
            logging.error(f"An error occurred during Vertex AI validation: {e}")
            return False, 0.0

async def main():
    """Main function to test the validation system."""
    # Example usage
    validation_system = TripleValidation()
    lead = {"id": "12345", "name": "John Doe", "email": "john.doe@example.com"}
    is_valid, confidence, summary = await validation_system.validate(lead)
    print(f"Validation result: {is_valid}, Confidence: {confidence:.2f}, Summary: {summary}")

if __name__ == "__main__":
    asyncio.run(main())
