import unittest

from evals.run_evals import matches_expectation, normalize


class EvalGraderTests(unittest.TestCase):
    def test_normalize_preserves_formatted_number_identity(self) -> None:
        self.assertIn("2850", normalize("The monthly rent is $2,850."))

    def test_exact_severity_remains_strict(self) -> None:
        verdict = {"status": "FLAGGED", "severity": "high", "claim": "Wrong rent"}
        expected = {"status": "FLAGGED", "severity": "medium", "contains": ["rent"]}

        self.assertFalse(matches_expectation(verdict, expected))

    def test_approved_severity_range_accepts_borderline_case(self) -> None:
        verdict = {"status": "FLAGGED", "severity": "high", "claim": "GBP is supported"}
        expected = {
            "status": "FLAGGED",
            "severity_any": ["medium", "high"],
            "contains": ["gbp"],
        }

        self.assertTrue(matches_expectation(verdict, expected))


if __name__ == "__main__":
    unittest.main()
