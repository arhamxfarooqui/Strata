"""Tests for the prompt guard anti-cheat classifier."""

import pytest
from app.services.prompt_guard import check_prompt, check_response_for_solution_leak


class TestPromptGuard:
    """Tests for prompt flagging heuristics."""

    def test_flags_give_me_the_solution(self):
        flagged, reason = check_prompt("Give me the solution to this problem")
        assert flagged is True
        assert "direct-answer" in reason.lower() or "pattern" in reason.lower()

    def test_flags_write_the_code(self):
        flagged, _ = check_prompt("Write the code for binary search")
        assert flagged is True

    def test_flags_solve_this_for_me(self):
        flagged, _ = check_prompt("Solve this for me please")
        assert flagged is True

    def test_flags_full_solution(self):
        flagged, _ = check_prompt("I need the full solution in C++")
        assert flagged is True

    def test_flags_complete_implementation(self):
        flagged, _ = check_prompt("Give me the complete implementation")
        assert flagged is True

    def test_flags_url_only(self):
        flagged, _ = check_prompt("https://codeforces.com/contest/1234/problem/A")
        assert flagged is True

    def test_flags_lazy_prompt(self):
        flagged, _ = check_prompt("solve https://codeforces.com/contest/1234/problem/A")
        assert flagged is True

    def test_allows_legitimate_question(self):
        flagged, _ = check_prompt("How should I think about this DP problem? I'm stuck on the state transition.")
        assert flagged is False

    def test_allows_concept_question(self):
        flagged, _ = check_prompt("Can you explain how segment trees work for range queries?")
        assert flagged is False

    def test_allows_debugging_question(self):
        flagged, _ = check_prompt("My BFS is giving wrong answer on test case 3. What am I missing conceptually?")
        assert flagged is False

    def test_allows_approach_question(self):
        flagged, _ = check_prompt("What approach should I use for this graph problem?")
        assert flagged is False


class TestResponseLeakDetection:
    """Tests for post-hoc solution leak detection in AI responses."""

    def test_detects_large_code_block(self):
        response = """Here's the approach:
```python
def solve():
    n = int(input())
    arr = list(map(int, input().split()))
    dp = [0] * (n + 1)
    for i in range(n):
        for j in range(i):
            dp[i] = max(dp[i], dp[j] + 1)
    print(max(dp))
    return
    extra_line = True

solve()
```"""
        assert check_response_for_solution_leak(response) is True

    def test_allows_short_snippet(self):
        response = """Think about the state like this:
```python
dp[i] = max(dp[j] + 1 for j in range(i))
```
The key insight is..."""
        assert check_response_for_solution_leak(response) is False

    def test_allows_no_code(self):
        response = "Think about using dynamic programming. The state should represent..."
        assert check_response_for_solution_leak(response) is False
