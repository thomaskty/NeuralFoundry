#!/usr/bin/env python3
"""
Test the populated data - asks tricky questions and verifies RAG system
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"


class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def load_scenarios():
    """Load test scenarios from file"""
    try:
        with open("test_scenarios.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"{Color.RED}❌ test_scenarios.json not found! Run populate_test_data.py first.{Color.RESET}")
        return None


def test_kb_retrieval(chat_id: str, questions: list):
    """Test knowledge base retrieval with tricky questions"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}TEST 1: KNOWLEDGE BASE RETRIEVAL{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}\n")

    results = {"passed": 0, "failed": 0}

    for i, test in enumerate(questions, 1):
        print(f"{Color.BOLD}[Question {i}/{len(questions)}]{Color.RESET}")
        print(f"{Color.YELLOW}Q: {test['question']}{Color.RESET}\n")

        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/messages",
            json={
                "role": "user",
                "content": test["question"]
            }
        )

        if response.status_code != 201:
            print(f"{Color.RED}❌ Request failed: {response.text}{Color.RESET}\n")
            results["failed"] += 1
            continue

        reply = response.json()["reply"]

        # Check if KB was used
        kb_used = "[using: knowledge base]" in reply.lower() or "knowledge base" in reply.lower()

        # Check if expected terms are in response
        found_terms = [term for term in test["expected_terms"] if term.lower() in reply.lower()]

        print(f"{Color.CYAN}A: {reply[:300]}...{Color.RESET}\n")

        print(f"{Color.BOLD}Analysis:{Color.RESET}")
        if kb_used:
            print(f"  {Color.GREEN}✓ KB context was used{Color.RESET}")
        else:
            print(f"  {Color.YELLOW}⚠ KB context not explicitly mentioned{Color.RESET}")

        print(f"  Expected KB: {Color.YELLOW}{test['expected_kb']}{Color.RESET}")
        print(
            f"  Found terms: {Color.GREEN}{', '.join(found_terms)}{Color.RESET} ({len(found_terms)}/{len(test['expected_terms'])})")

        if len(found_terms) >= len(test["expected_terms"]) // 2:
            print(f"  {Color.GREEN}✅ PASSED - Answer is relevant!{Color.RESET}")
            results["passed"] += 1
        else:
            print(f"  {Color.RED}❌ FAILED - Answer may not be using correct KB{Color.RESET}")
            results["failed"] += 1

        print(f"{Color.CYAN}{'-' * 70}{Color.RESET}\n")
        time.sleep(1)

    return results


def test_chat_history(conversations: list, chat_ids: list):
    """Test if system uses chat history context"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}TEST 2: CHAT HISTORY CONTEXT{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}\n")

    results = {"passed": 0, "failed": 0}

    for i, (conv, chat_id) in enumerate(zip(conversations, chat_ids), 1):
        print(f"{Color.BOLD}[Chat {i}/{len(conversations)}] {conv['title']}{Color.RESET}\n")

        # Show conversation history
        print(f"{Color.CYAN}Previous conversation:{Color.RESET}")
        for msg in conv["messages"][:-1]:
            role_color = Color.YELLOW if msg["role"] == "user" else Color.GREEN
            print(f"  {role_color}{msg['role']}: {msg['content'][:100]}...{Color.RESET}")

        # Send incomplete last message
        last_message = conv["messages"][-1]
        print(f"\n{Color.YELLOW}Now asking: {last_message['content']}{Color.RESET}")
        print(f"{Color.MAGENTA}(This should reference previous conversation){Color.RESET}\n")

        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/messages",
            json=last_message
        )

        if response.status_code != 201:
            print(f"{Color.RED}❌ Request failed: {response.text}{Color.RESET}\n")
            results["failed"] += 1
            continue

        reply = response.json()["reply"]

        # Check if conversation history was used
        history_used = (
                "[using: conversation history]" in reply.lower() or
                "conversation" in reply.lower() or
                "mentioned" in reply.lower() or
                "discussed" in reply.lower()
        )

        print(f"{Color.CYAN}Response: {reply[:400]}...{Color.RESET}\n")

        print(f"{Color.BOLD}Analysis:{Color.RESET}")
        if history_used:
            print(f"  {Color.GREEN}✓ Conversation history was used{Color.RESET}")
            results["passed"] += 1
        else:
            print(f"  {Color.YELLOW}⚠ Not clear if history was used{Color.RESET}")
            results["failed"] += 1

        print(f"{Color.CYAN}{'-' * 70}{Color.RESET}\n")
        time.sleep(1)

    return results


def test_combined_context(chat_id: str):
    """Test if system can use both KB and chat history together"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}TEST 3: COMBINED CONTEXT (KB + CHAT HISTORY){Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}\n")

    # First, have a conversation about FastAPI
    print(f"{Color.BOLD}Setting up conversation context...{Color.RESET}\n")

    messages = [
        "Tell me about FastAPI authentication",
        "What about the middleware order?",
        "Now, can you also explain the database connection pooling best practices we discussed earlier?"
    ]

    for msg in messages[:-1]:
        print(f"{Color.YELLOW}User: {msg}{Color.RESET}")
        response = requests.post(
            f"{BASE_URL}/chats/{chat_id}/messages",
            json={"role": "user", "content": msg}
        )
        if response.status_code == 201:
            reply = response.json()["reply"]
            print(f"{Color.GREEN}Assistant: {reply[:150]}...{Color.RESET}\n")
        time.sleep(1)

    # Now ask a question that requires both KB and chat history
    print(f"{Color.BOLD}Now testing combined context:{Color.RESET}\n")

    last_question = messages[-1]
    print(f"{Color.YELLOW}User: {last_question}{Color.RESET}")
    print(f"{Color.MAGENTA}(This requires BOTH KB docs AND previous conversation){Color.RESET}\n")

    response = requests.post(
        f"{BASE_URL}/chats/{chat_id}/messages",
        json={"role": "user", "content": last_question}
    )

    if response.status_code != 201:
        print(f"{Color.RED}❌ Request failed: {response.text}{Color.RESET}")
        return {"passed": 0, "failed": 1}

    reply = response.json()["reply"]
    print(f"{Color.CYAN}Response: {reply[:500]}...{Color.RESET}\n")

    # Check if both sources were used
    kb_used = "knowledge base" in reply.lower()
    history_used = "conversation" in reply.lower() or "discussed" in reply.lower()
    mentions_auth = "auth" in reply.lower() or "oauth" in reply.lower()
    mentions_middleware = "middleware" in reply.lower()
    mentions_pooling = "pool" in reply.lower() or "connection" in reply.lower()

    print(f"{Color.BOLD}Analysis:{Color.RESET}")
    print(f"  KB context used: {Color.GREEN + '✓' if kb_used else Color.RED + '✗'}{Color.RESET}")
    print(f"  Chat history used: {Color.GREEN + '✓' if history_used else Color.RED + '✗'}{Color.RESET}")
    print(f"  Mentions authentication: {Color.GREEN + '✓' if mentions_auth else Color.RED + '✗'}{Color.RESET}")
    print(f"  Mentions middleware: {Color.GREEN + '✓' if mentions_middleware else Color.RED + '✗'}{Color.RESET}")
    print(f"  Mentions connection pooling: {Color.GREEN + '✓' if mentions_pooling else Color.RED + '✗'}{Color.RESET}")

    score = sum([kb_used, history_used, mentions_auth, mentions_middleware, mentions_pooling])

    if score >= 3:
        print(f"\n  {Color.GREEN}✅ PASSED - Using both KB and chat history!{Color.RESET}")
        return {"passed": 1, "failed": 0}
    else:
        print(f"\n  {Color.YELLOW}⚠ PARTIAL - May not be using all context sources{Color.RESET}")
        return {"passed": 0, "failed": 1}


def print_final_summary(kb_results, history_results, combined_results):
    """Print final test summary"""
    print(f"\n{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.GREEN}📊 FINAL TEST SUMMARY{Color.RESET}")
    print(f"{Color.BOLD}{Color.CYAN}{'=' * 70}{Color.RESET}\n")

    total_passed = kb_results["passed"] + history_results["passed"] + combined_results["passed"]
    total_failed = kb_results["failed"] + history_results["failed"] + combined_results["failed"]
    total_tests = total_passed + total_failed

    pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    print(f"{Color.BOLD}Test Results:{Color.RESET}")
    print(
        f"  Knowledge Base Retrieval: {Color.GREEN}{kb_results['passed']}{Color.RESET}/{kb_results['passed'] + kb_results['failed']} passed")
    print(
        f"  Chat History Context: {Color.GREEN}{history_results['passed']}{Color.RESET}/{history_results['passed'] + history_results['failed']} passed")
    print(
        f"  Combined Context: {Color.GREEN}{combined_results['passed']}{Color.RESET}/{combined_results['passed'] + combined_results['failed']} passed")

    print(f"\n{Color.BOLD}Overall:{Color.RESET}")
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {Color.GREEN}{total_passed}{Color.RESET}")
    print(f"  Failed: {Color.RED}{total_failed}{Color.RESET}")
    print(f"  Pass Rate: {Color.YELLOW}{pass_rate:.1f}%{Color.RESET}")

    if pass_rate >= 80:
        print(f"\n  {Color.GREEN}🎉 EXCELLENT! Your RAG system is working great!{Color.RESET}")
    elif pass_rate >= 60:
        print(f"\n  {Color.YELLOW}👍 GOOD! Some improvements possible but functional.{Color.RESET}")
    else:
        print(f"\n  {Color.RED}⚠️  NEEDS WORK - Check thresholds and KB content.{Color.RESET}")

    print(f"\n{Color.CYAN}{'=' * 70}{Color.RESET}\n")


def main():
    """Main test function"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}🧪 TESTING POPULATED DATA{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{'=' * 70}{Color.RESET}\n")

    # Load test scenarios
    scenarios = load_scenarios()
    if not scenarios:
        return

    print(f"{Color.GREEN}✅ Loaded test scenarios{Color.RESET}")
    print(f"  User ID: {scenarios['user_id']}")
    print(f"  KB ID: {scenarios['kb_id']}")
    print(f"  Chat IDs: {len(scenarios['chat_ids'])} chats")

    # Test 1: KB Retrieval
    kb_results = test_kb_retrieval(
        scenarios['chat_ids'][0],
        scenarios['tricky_questions']
    )

    # Test 2: Chat History
    history_results = test_chat_history(
        scenarios['conversations'],
        scenarios['chat_ids']
    )

    # Test 3: Combined Context
    # Create a fresh chat for this test
    print(f"\n{Color.BOLD}Creating fresh chat for combined context test...{Color.RESET}")
    response = requests.post(
        f"{BASE_URL}/users/{scenarios['user_id']}/chats",
        json={"title": "Combined Context Test"}
    )
    if response.status_code == 201:
        test_chat_id = response.json()["chat_id"]
        # Attach KB
        requests.post(f"{BASE_URL}/chats/{test_chat_id}/knowledge-bases/{scenarios['kb_id']}")
        combined_results = test_combined_context(test_chat_id)
    else:
        print(f"{Color.RED}❌ Failed to create test chat{Color.RESET}")
        combined_results = {"passed": 0, "failed": 1}

    # Print summary
    print_final_summary(kb_results, history_results, combined_results)

    # Save results
    results = {
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
        "kb_retrieval": kb_results,
        "chat_history": history_results,
        "combined_context": combined_results
    }

    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"{Color.GREEN}✅ Results saved to test_results.json{Color.RESET}\n")


if __name__ == "__main__":
    main()