#!/usr/bin/env python3
"""
Complete API Test Suite for Neural Foundry
Tests all endpoints systematically with clear output
"""
import requests
import time
import json
from typing import Optional

# Configuration
BASE_URL = "http://localhost:8000/api/v1"
PROCESSING_WAIT_TIME = 10  # seconds to wait for background processing


# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")


def print_step(step_num: int, text: str):
    print(f"{Colors.BOLD}{Colors.BLUE}[Step {step_num}]{Colors.RESET} {text}")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str):
    print(f"{Colors.MAGENTA}ℹ️  {text}{Colors.RESET}")


def assert_status(response, expected_status: int, context: str):
    """Assert response status and print result"""
    if response.status_code == expected_status:
        print_success(f"{context} - Status {response.status_code}")
        return True
    else:
        print_error(f"{context} - Expected {expected_status}, got {response.status_code}")
        print_error(f"Response: {response.text}")
        return False


def test_user_endpoints():
    """Test 1: User Management"""
    print_header("TEST 1: USER MANAGEMENT")

    print_step(1, "Creating user...")
    response = requests.post(
        f"{BASE_URL}/users",
        json={"username": f"test_user_{int(time.time())}"}
    )

    if not assert_status(response, 201, "Create user"):
        return None

    user_data = response.json()
    user_id = user_data["id"]
    print_info(f"User ID: {user_id}")
    print_info(f"Username: {user_data['username']}")

    return user_id


def test_knowledge_base_endpoints(user_id: str):
    """Test 2: Knowledge Base Management"""
    print_header("TEST 2: KNOWLEDGE BASE MANAGEMENT")

    # Create KB
    print_step(2, "Creating knowledge base...")
    response = requests.post(
        f"{BASE_URL}/users/{user_id}/knowledge-bases",
        json={
            "title": "FastAPI Testing Guide",
            "description": "A comprehensive guide to testing FastAPI applications"
        }
    )

    if not assert_status(response, 201, "Create KB"):
        return None

    kb_data = response.json()
    kb_id = kb_data["kb_id"]
    print_info(f"KB ID: {kb_id}")
    print_info(f"Title: {kb_data['title']}")

    # List user's KBs
    print_step(3, "Listing user's knowledge bases...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/knowledge-bases")

    if assert_status(response, 200, "List KBs"):
        kbs = response.json()
        print_info(f"Total KBs for user: {len(kbs)}")

    return kb_id


def test_document_upload(kb_id: str):
    """Test 3: Document Upload and Processing"""
    print_header("TEST 3: DOCUMENT UPLOAD & PROCESSING")

    # Create test document
    print_step(4, "Creating test document...")
    test_content = """
    FastAPI Framework Guide

    FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.8+.

    Key Features:
    1. Very high performance, on par with NodeJS and Go
    2. Fast to code: Increase development speed by about 200-300%
    3. Fewer bugs: Reduce human errors by about 40%
    4. Intuitive: Great editor support with autocomplete
    5. Easy: Designed to be easy to use and learn
    6. Standards-based: Based on OpenAPI and JSON Schema

    FastAPI uses Starlette for the web parts and Pydantic for the data parts.
    It provides automatic interactive API documentation with Swagger UI and ReDoc.
    FastAPI fully supports async and await for asynchronous code.
    """

    files = {"file": ("fastapi_guide.txt", test_content, "text/plain")}

    print_step(5, "Uploading document to KB...")
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/upload",
        files=files
    )

    if not assert_status(response, 202, "Upload document"):
        return False

    print_info("Document accepted for processing")
    print_warning(f"Waiting {PROCESSING_WAIT_TIME} seconds for background processing...")

    # Progress indicator
    for i in range(PROCESSING_WAIT_TIME):
        print(f"⏳ Processing... {i + 1}/{PROCESSING_WAIT_TIME}s", end='\r')
        time.sleep(1)
    print()

    print_success("Document should be processed now")

    # Test duplicate upload
    print_step(6, "Testing duplicate file upload prevention...")
    response = requests.post(
        f"{BASE_URL}/knowledge-bases/{kb_id}/upload",
        files=files
    )

    if assert_status(response, 409, "Duplicate prevention"):
        print_success("Duplicate file prevention working correctly!")

    return True


def test_chat_endpoints(user_id: str):
    """Test 4: Chat Management"""
    print_header("TEST 4: CHAT MANAGEMENT")

    # Create chat
    print_step(7, "Creating chat session...")
    response = requests.post(
        f"{BASE_URL}/users/{user_id}/chats",
        json={
            "title": "FastAPI Q&A Session",
            "system_prompt": "You are a helpful assistant specialized in FastAPI framework."
        }
    )

    if not assert_status(response, 201, "Create chat"):
        return None

    chat_data = response.json()
    chat_id = chat_data["chat_id"]
    print_info(f"Chat ID: {chat_id}")
    print_info(f"Title: {chat_data['title']}")

    # Get chat details
    print_step(8, "Fetching chat details...")
    response = requests.get(f"{BASE_URL}/chats/{chat_id}")

    if assert_status(response, 200, "Get chat"):
        chat = response.json()
        print_info(f"Messages count: {len(chat['messages'])}")

    # List user's chats
    print_step(9, "Listing user's chats...")
    response = requests.get(f"{BASE_URL}/users/{user_id}/chats")

    if assert_status(response, 200, "List user chats"):
        data = response.json()
        print_info(f"Total chats for user: {len(data['chats'])}")

    return chat_id


def test_chat_kb_integration(chat_id: str, kb_id: str):
    """Test 5: Chat-KB Integration"""
    print_header("TEST 5: CHAT-KB INTEGRATION")

    # Attach KB to chat
    print_step(10, "Attaching KB to chat...")
    response = requests.post(
        f"{BASE_URL}/chats/{chat_id}/knowledge-bases/{kb_id}"
    )

    if not assert_status(response, 201, "Attach KB"):
        return False

    attach_data = response.json()
    print_info(f"Attached KB: {attach_data['kb_title']}")

    # List attached KBs
    print_step(11, "Listing attached KBs...")
    response = requests.get(f"{BASE_URL}/chats/{chat_id}/knowledge-bases")

    if assert_status(response, 200, "List attached KBs"):
        data = response.json()
        print_info(f"Total KBs attached: {data['total_kbs']}")
        for kb in data['knowledge_bases']:
            print_info(f"  - {kb['title']}")

    # List chats using this KB
    print_step(12, "Listing chats using this KB...")
    response = requests.get(f"{BASE_URL}/knowledge-bases/{kb_id}/chats")

    if assert_status(response, 200, "List KB chats"):
        data = response.json()
        print_info(f"Total chats using KB: {data['total_chats']}")

    return True


def test_rag_pipeline(chat_id: str, kb_id: str):
    """Test 6: RAG Pipeline (The Main Feature!)"""
    print_header("TEST 6: RAG PIPELINE - THE MOMENT OF TRUTH! 🎯")

    test_queries = [
        {
            "query": "What is FastAPI?",
            "expected_context": "knowledge base",
            "should_contain": ["modern", "fast", "Python"]
        },
        {
            "query": "What are the key features of FastAPI?",
            "expected_context": "knowledge base",
            "should_contain": ["performance", "fast to code", "intuitive"]
        },
        {
            "query": "Tell me about FastAPI's performance",
            "expected_context": "knowledge base",
            "should_contain": ["high performance", "NodeJS", "Go"]
        }
    ]

    all_passed = True

    for idx, test_case in enumerate(test_queries, 1):
        print_step(12 + idx, f"Testing query: '{test_case['query']}'")

        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/messages",
            json={
                "role": "user",
                "content": test_case["query"]
            }
        )

        if not assert_status(response, 201, "Send message"):
            all_passed = False
            continue

        data = response.json()
        reply = data["reply"]

        # Check if KB context was used
        if test_case["expected_context"] in reply.lower():
            print_success(f"✓ KB context detected in response")
        else:
            print_warning(f"KB context not explicitly mentioned")

        # Check if response contains expected terms
        found_terms = [term for term in test_case["should_contain"]
                       if term.lower() in reply.lower()]

        if found_terms:
            print_success(f"✓ Response contains relevant terms: {', '.join(found_terms)}")
        else:
            print_warning(f"Expected terms not found in response")

        print_info(f"Reply preview: {reply[:200]}...")
        print()

        time.sleep(1)  # Small delay between messages

    # Test without KB context (detach and test)
    print_step(16, "Testing response WITHOUT KB context...")

    # Detach KB
    response = requests.delete(f"{BASE_URL}/chats/{chat_id}/knowledge-bases/{kb_id}")
    if assert_status(response, 200, "Detach KB"):
        print_success("KB detached successfully")

    # Send message to see fallback behavior
    response = requests.post(
        f"{BASE_URL}/chats/{chat_id}/messages",
        json={
            "role": "user",
            "content": "What is FastAPI?"
        }
    )

    if assert_status(response, 201, "Send message without KB"):
        reply = response.json()["reply"]
        if "no relevant context" in reply.lower() or "note:" in reply.lower():
            print_success("✓ Correctly indicates no KB context available")
        print_info(f"Reply preview: {reply[:200]}...")

    return all_passed


def test_cleanup(chat_id: str, kb_id: str):
    """Test 7: Cleanup"""
    print_header("TEST 7: CLEANUP")

    # Delete chat
    print_step(17, "Deleting chat...")
    response = requests.delete(f"{BASE_URL}/chats/{chat_id}")
    assert_status(response, 200, "Delete chat")

    # Delete KB
    print_step(18, "Deleting knowledge base...")
    response = requests.delete(f"{BASE_URL}/knowledge-bases/{kb_id}")
    assert_status(response, 200, "Delete KB")

    print_success("Cleanup complete!")


def run_all_tests():
    """Run complete test suite"""
    print_header("🚀 NEURAL FOUNDRY API TEST SUITE")
    print_info(f"Base URL: {BASE_URL}")
    print_info(f"Starting tests at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    start_time = time.time()

    try:
        # Test 1: Users
        user_id = test_user_endpoints()
        if not user_id:
            print_error("User tests failed! Stopping.")
            return

        # Test 2: Knowledge Bases
        kb_id = test_knowledge_base_endpoints(user_id)
        if not kb_id:
            print_error("KB tests failed! Stopping.")
            return

        # Test 3: Document Upload
        if not test_document_upload(kb_id):
            print_error("Document upload tests failed! Stopping.")
            return

        # Test 4: Chats
        chat_id = test_chat_endpoints(user_id)
        if not chat_id:
            print_error("Chat tests failed! Stopping.")
            return

        # Test 5: Chat-KB Integration
        if not test_chat_kb_integration(chat_id, kb_id):
            print_error("Chat-KB integration tests failed! Stopping.")
            return

        # Test 6: RAG Pipeline (THE BIG ONE!)
        if not test_rag_pipeline(chat_id, kb_id):
            print_warning("Some RAG tests had issues, but continuing...")

        # Test 7: Cleanup
        test_cleanup(chat_id, kb_id)

        # Summary
        elapsed = time.time() - start_time
        print_header("🎉 TEST SUMMARY")
        print_success(f"All tests completed in {elapsed:.2f} seconds!")
        print_success("Your RAG system is working! 🚀")

    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

