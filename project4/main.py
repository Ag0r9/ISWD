from typing import Dict

from utils import read_csv

import pandas as pd
import pulp as pl
from pulp import LpProblem, LpMaximize, LpVariable, LpStatus


def define_efficiencies(df: pd.DataFrame, super_eff: bool = False) -> Dict[str, float]:
    i1 = LpVariable("i1", lowBound=0, cat="Continuous")
    i2 = LpVariable("i2", lowBound=0, cat="Continuous")
    i3 = LpVariable("i3", lowBound=0, cat="Continuous")
    i4 = LpVariable("i4", lowBound=0, cat="Continuous")
    o1 = LpVariable("o1", lowBound=0, cat="Continuous")
    o2 = LpVariable("o2", lowBound=0, cat="Continuous")
    efficiency: Dict[str, float] = {}
    airports = df.index.tolist()
    for chosen_airport_name in airports:
        problem = LpProblem("problem", LpMaximize)
        airport: pd.Series = df.loc[chosen_airport_name]
        # Objective Function
        problem += airport["o1"] * o1 + airport["o2"] * o2, "Objective Function"
        # Constraints
        problem += (
            airport["i1"] * i1
            + airport["i2"] * i2
            + airport["i3"] * i3
            + airport["i4"] * i4
            == 1,
            "airport Constraint",
        )
        airports_within = airports.copy()
        if super_eff:
            airports_within.remove(chosen_airport_name)
        for airport_name in airports_within:
            problem += (
                df.loc[airport_name, "i1"] * i1
                + df.loc[airport_name, "i2"] * i2
                + df.loc[airport_name, "i3"] * i3
                + df.loc[airport_name, "i4"] * i4
                >= df.loc[airport_name, "o1"] * o1 + df.loc[airport_name, "o2"] * o2,
                f"{airport_name} Constraint",
            )
        for var, var_name in zip(
            [i1, i2, i3, i4, o1, o2], ["i1", "i2", "i3", "i4", "o1", "o2"]
        ):
            problem += var >= 0, f"{var_name} positive Constraint"
        # Solver
        print("Current Status: ", LpStatus[problem.status])
        problem.solve()
        efficiency[chosen_airport_name] = round(
            airport["o1"] * o1.varValue + airport["o2"] * o2.varValue, 3
        )
    return efficiency


def calculate_hcu(df: pd.DataFrame) -> pd.DataFrame:
    df_hcu = pd.DataFrame()
    return df_hcu


def main():
    df_input: pd.DataFrame = read_csv("inputs.csv")
    df_output: pd.DataFrame = read_csv("outputs.csv")
    df = pd.concat([df_input, df_output], axis=1)
    efficiencies: Dict[str, float] = define_efficiencies(df)
    print(efficiencies)
    super_efficiencies: Dict[str, float] = define_efficiencies(df, True)
    print(super_efficiencies)


if __name__ == "__main__":
    main()
