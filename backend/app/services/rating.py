"""
Strata Rating algorithm — unified cross-domain score.
"""

import math


def calculate_axios_rating(
    cf_rating: int, cf_solved: int, github_repos: int, github_prs: int = 0
) -> int:
    """
    Calculate the unified Strata/Axios rating.

    Formula:
        (cf_rating × 0.5) + (cf_solved × 5) + (github_repos × 20) + (github_prs × 50)
    """
    normalized_cf = max(0.0, float(cf_rating))
    score = (
        (normalized_cf * 0.5)
        + (float(cf_solved) * 5.0)
        + (float(github_repos) * 20.0)
        + (float(github_prs) * 50.0)
    )
    return round(score)
