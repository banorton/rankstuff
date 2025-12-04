"""
Chart service - Returns hardcoded visualization data for school project.
"""

from models.charts import (
    AlgorithmComparisonChart,
    AlgorithmScore,
    VoteDistributionChart,
    OptionDistribution,
)


class ChartService:
    """Service for chart data."""

    def get_algorithm_comparison(self) -> AlgorithmComparisonChart:
        """
        Returns data showing how the same votes produce different winners
        under Plurality, Borda Count, and Instant Runoff Voting.

        Scenario: 5 voters ranking 3 candidates (A, B, C)
        - Voter 1: A > B > C
        - Voter 2: A > B > C
        - Voter 3: B > C > A
        - Voter 4: C > B > A
        - Voter 5: C > B > A
        """
        return AlgorithmComparisonChart(
            title="Same Votes, Different Winners",
            description=(
                "This chart demonstrates a key insight in voting theory: the same set of "
                "voter preferences can produce different winners depending on which voting "
                "algorithm is used. Here, 5 voters rank 3 candidates. Under Plurality voting "
                "(first choice only), Candidate A wins with 2 first-place votes. Under Borda "
                "Count (points for each rank), Candidate B wins by accumulating the most total "
                "points. Under Instant Runoff Voting (eliminate lowest, redistribute), "
                "Candidate C wins after A is eliminated and votes transfer."
            ),
            source_url="https://en.wikipedia.org/wiki/Comparison_of_electoral_systems",
            data=[
                AlgorithmScore(
                    algorithm="Plurality",
                    winner="A",
                    scores={"A": 2, "B": 1, "C": 2},
                ),
                AlgorithmScore(
                    algorithm="Borda Count",
                    winner="B",
                    scores={"A": 6, "B": 10, "C": 9},
                ),
                AlgorithmScore(
                    algorithm="Instant Runoff",
                    winner="C",
                    scores={"A": 0, "B": 2, "C": 3},
                ),
            ],
        )

    def get_vote_distribution(self) -> VoteDistributionChart:
        """
        Returns data showing the distribution of rankings across options.

        Based on a hypothetical poll with 100 voters ranking 3 options.
        """
        return VoteDistributionChart(
            title="Ranking Distribution by Option",
            description=(
                "This chart shows how voters distributed their rankings across three options "
                "in a ranked-choice poll with 100 participants. Option A received the most "
                "first-place votes (40%) but was polarizing with many third-place votes. "
                "Option B was the consensus choice, rarely ranked last. Option C was "
                "consistently middle-ranked. This pattern illustrates why Borda Count often "
                "selects compromise candidates that are broadly acceptable rather than "
                "polarizing favorites."
            ),
            source_url="https://en.wikipedia.org/wiki/Borda_count",
            data=[
                OptionDistribution(option="Option A", first=40, second=20, third=40),
                OptionDistribution(option="Option B", first=30, second=55, third=15),
                OptionDistribution(option="Option C", first=30, second=25, third=45),
            ],
        )
