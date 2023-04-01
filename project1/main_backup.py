from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
from pulp import LpMaximize, LpProblem, LpStatus, LpVariable


class UTA:
    def __init__(self):
        self.data = self.load_data("Nuclear waste management.csv")
        self.criterias: List[np.ndarray] = []
        self.min_values: List[int] = []
        self.ranking: Dict = {}
        self.all_l = []

    def main(self):
        self.create_solver()
        self.rank_data()
        self.print_ranking()
        self.plot_uts_crit()


    @classmethod
    def load_data(cls, filename: str) -> np.ndarray:
        return np.genfromtxt(filename, delimiter=",")[1:, 1:]

    def plot_uts_crit(self):
        fig, axes = plt.subplots(2, 2, figsize=(15, 15))
        for i, ax in enumerate(axes.flat):
            ax.plot([criteria.name.split("_")[1] for criteria in self.all_l[i]],
                [round(criteria.value()) for criteria in self.all_l[i]],
            )
            ax.set_title(f"C {i + 1}")
        plt.show()

    def print_ranking(self):
        for i, action in enumerate(self.ranking, 1):
            print(f"{i}: {action}")

    def rank_data(self):
        for row_id in range(self.data.shape[0]):
            score = 0
            for col_id in range(len(self.criterias)):
                value = int(self.data[row_id, col_id] * 100) - self.min_values[col_id]
                score += (
                    self.criterias[col_id][value]
                    if value < self.criterias[col_id].shape[0]
                    else self.criterias[col_id][-1]
                )
            self.ranking[row_id + 1] = score
        self.ranking = sorted(self.ranking.items(), key=lambda x: x[1], reverse=True)

    def create_solver(self):
        # comparing_variants = ((11, 18), (14, 17), (1, 11), (4, 17), (1, 4))
        model = LpProblem(name="nwm", sense=LpMaximize)
        epsilon = LpVariable(name="eps", lowBound=0, cat="Continuous")

        v1_32 = LpVariable(name="v1_32", lowBound=0, cat="Continuous")
        v1_60 = LpVariable(name="v1_60", lowBound=0, cat="Continuous")
        v1_61 = LpVariable(name="v1_61", lowBound=0, cat="Continuous")
        v1_62 = LpVariable(name="v1_62", lowBound=0, cat="Continuous")
        v1_64 = LpVariable(name="v1_64", lowBound=0, cat="Continuous")
        v1_68 = LpVariable(name="v1_68", lowBound=0, cat="Continuous")
        v1_69 = LpVariable(name="v1_69", lowBound=0, cat="Continuous")
        v1_76 = LpVariable(name="v1_76", lowBound=0, cat="Continuous")
        v1_100 = LpVariable(name="v1_100", lowBound=0, cat="Continuous")

        v2_03 = LpVariable(name="v2_03", lowBound=0, cat="Continuous")
        v2_06 = LpVariable(name="v2_06", lowBound=0, cat="Continuous")
        v2_40 = LpVariable(name="v2_40", lowBound=0, cat="Continuous")
        v2_44 = LpVariable(name="v2_44", lowBound=0, cat="Continuous")
        v2_45 = LpVariable(name="v2_45", lowBound=0, cat="Continuous")
        v2_49 = LpVariable(name="v2_49", lowBound=0, cat="Continuous")
        v2_54 = LpVariable(name="v2_54", lowBound=0, cat="Continuous")
        v2_93 = LpVariable(name="v2_93", lowBound=0, cat="Continuous")
        v2_100 = LpVariable(name="v2_100", lowBound=0, cat="Continuous")

        v3_00 = LpVariable(name="v3_00", lowBound=0, cat="Continuous")
        v3_38 = LpVariable(name="v3_38", lowBound=0, cat="Continuous")
        v3_54 = LpVariable(name="v3_54", lowBound=0, cat="Continuous")
        v3_56 = LpVariable(name="v3_56", lowBound=0, cat="Continuous")
        v3_57 = LpVariable(name="v3_57", lowBound=0, cat="Continuous")
        v3_65 = LpVariable(name="v3_65", lowBound=0, cat="Continuous")
        v3_100 = LpVariable(name="v3_100", lowBound=0, cat="Continuous")

        v4_49 = LpVariable(name="v4_49", lowBound=0, cat="Continuous")
        v4_50 = LpVariable(name="v4_50", lowBound=0, cat="Continuous")
        v4_54 = LpVariable(name="v4_54", lowBound=0, cat="Continuous")
        v4_60 = LpVariable(name="v4_60", lowBound=0, cat="Continuous")
        v4_61 = LpVariable(name="v4_61", lowBound=0, cat="Continuous")
        v4_73 = LpVariable(name="v4_73", lowBound=0, cat="Continuous")
        v4_100 = LpVariable(name="v4_100", lowBound=0, cat="Continuous")

        all_1: List[LpVariable] = [
            v1_32,
            v1_60,
            v1_61,
            v1_62,
            v1_64,
            v1_68,
            v1_69,
            v1_76,
            v1_100,
        ]
        all_2: List[LpVariable] = [
            v2_03,
            v2_06,
            v2_40,
            v2_44,
            v2_45,
            v2_49,
            v2_54,
            v2_93,
            v2_100,
        ]
        all_3: List[LpVariable] = [v3_00, v3_38, v3_54, v3_56, v3_57, v3_65, v3_100]
        all_4: List[LpVariable] = [v4_49, v4_50, v4_54, v4_60, v4_61, v4_73, v4_100]
        self.all_l: List[List[LpVariable]] = [all_1, all_2, all_3, all_4]

        model += (
            v1_61 + v2_54 + v3_38 + v4_49 >= v1_76 + v2_06 + v3_100 + v4_60 + epsilon,
            "11_greater_than_18",
        )
        model += (
            v1_69 + v2_49 + v3_56 + v4_61 == v1_68 + v2_40 + v3_65 + v4_60,
            "14_equal_17",
        )
        model += (
            v1_60 + v2_93 + v3_00 + v4_73 >= v1_61 + v2_54 + v3_38 + v4_49 + epsilon,
            "1_greater_than_11",
        )
        model += (
            v1_100 + v2_45 + v3_57 + v4_49 >= v1_62 + v2_40 + v3_56 + v4_50 + epsilon,
            "3_greater_than_5",
        )
        model += (
            v1_100 + v2_45 + v3_57 + v4_49 >= v1_64 + v2_44 + v3_54 + v4_54 + epsilon,
            "3_greater_than_8",
        )

        model += (v1_32 + v2_03 + v3_00 + v4_49 == 1, "normalization_max")
        model += (v1_100 == 0, "min_1")
        model += (v2_100 == 0, "min_2")
        model += (v3_100 == 0, "min_3")
        model += (v4_100 == 0, "min_4")

        for c in [all_1, all_2, all_3, all_4]:
            for c_id in range(1, len(c)):
                model += c[c_id - 1] >= c[c_id]

        for c in self.all_l:
            for value in c:
                model += value >= 0

        model += epsilon

        model.solve()
        print(f"status: {model.status}, {LpStatus[model.status]}")
        print(f"objective: {model.objective.value()}")

        # for c in self.all_l:
        #     for value in c:
        #         print(value.name, value.value())

        for c in self.all_l:
            arr = np.array([])
            self.min_values.append(int(c[0].name.split("_")[1]))
            for i in range(1, len(c)):
                arr = np.concatenate(
                    (
                        arr,
                        np.linspace(
                            start=c[i-1].value(),
                            stop=c[i].value(),
                            num=(
                                int(c[i].name.split("_")[1])
                                - int(c[i-1].name.split("_")[1])
                            ),
                        ),
                    )
                )
            self.criterias.append(arr)


if __name__ == "__main__":
    UTA().main()
