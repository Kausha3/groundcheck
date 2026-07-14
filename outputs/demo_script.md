# GroundCheck demo script

## 0:00-0:15 - Problem

"AI agent output can look completely professional while quietly changing a number or inventing a requirement. GroundCheck acts like unit tests for that output before a human trusts it."

## 0:15-0:35 - Inputs

Show the lease source on the left and the generated summary on the right.

"I gave GroundCheck a real lease document and an AI-generated summary that claims to be based on it. The summary looks plausible, but it contains three planted errors."

## 0:35-1:05 - Run the check

Click **Run GroundCheck** and let the verdicts appear.

"The rent is inflated by $400, the summary invents a pet policy that does not exist, and it doubles the parking spots. GroundCheck catches all three with appropriate severity ratings. It also passes the four accurate claims, so it is not simply rejecting everything."

## 1:05-1:35 - Developer workflow

Select the API specification example and run it.

"This is not limited to leases. Here it checks an agent-generated API summary against the actual specification and catches changed authentication, currency, and refund requirements."

Show **Copy report** and **Export JSON**.

"The results can be copied for a review or exported as structured JSON for a CI pipeline, evaluation harness, or agent workflow."

## 1:35-2:05 - Implementation

"GroundCheck is a full-stack FastAPI application built with Codex. The backend calls GPT-5.6 through the OpenAI Responses API and requires a typed claim-by-claim result: status, severity, confidence, explanation, and source evidence. The frontend then sorts contradictions first and renders the review."

## 2:05-2:25 - Close

"GroundCheck prevents agent output that sounds right but is not. It is a small review gate today, with a clear path toward pull-request checks, document pipelines, and automated evaluations."

End on the results screen with the public URL visible.
