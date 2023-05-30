from typing import Dict, List

from utils import read_csv

import pandas as pd
import pulp as pl
from pulp import LpProblem, LpMaximize, LpMinimize, LpVariable, LpStatus


def calculate_efficiencies(
    df: pd.DataFrame, super_eff: bool = False
) -> Dict[str, float]:
    i1 = LpVariable("i1", lowBound=0, cat="Continuous")
    i2 = LpVariable("i2", lowBound=0, cat="Continuous")
    i3 = LpVariable("i3", lowBound=0, cat="Continuous")
    i4 = LpVariable("i4", lowBound=0, cat="Continuous")
    o1 = LpVariable("o1", lowBound=0, cat="Continuous")
    o2 = LpVariable("o2", lowBound=0, cat="Continuous")
    efficiencies: Dict[str, float] = {}
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
        # Solver
        # print("Current Status: ", LpStatus[problem.status])
        problem.solve()
        efficiencies[chosen_airport_name] = round(
            airport["o1"] * o1.varValue + airport["o2"] * o2.varValue, 3
        )
    return efficiencies


def calculate_hcu(df: pd.DataFrame) -> pd.DataFrame:
    airports: List[str] = df.index.tolist()
    lambdas: Dict[str, LpVariable] = {
        airport_name: LpVariable(airport_name, lowBound=0, cat="Continuous")
        for airport_name in airports
    }
    theta = LpVariable("theta", lowBound=0, cat="Continuous")
    hcu: Dict[str, List[float]] = {}
    for chosen_airport_name in airports:
        problem = LpProblem("problem", LpMinimize)
        airport: pd.Series = df.loc[chosen_airport_name]
        # Objective Function
        problem += theta, "Objective Function"
        for chosen_input in ["i1", "i2", "i3", "i4"]:
            problem += (
                sum(
                    [
                        df.loc[airport_name, chosen_input] * airport_lambda
                        for airport_name, airport_lambda in lambdas.items()
                    ]
                )
                <= theta * airport[chosen_input]
            )
        for chosen_output in ["o1", "o2"]:
            problem += (
                sum(
                    [
                        df.loc[airport_name, chosen_output] * airport_lambda
                        for airport_name, airport_lambda in lambdas.items()
                    ]
                )
                >= airport[chosen_output]
            )
        # Solver
        print("Current Status: ", LpStatus[problem.status])
        problem.solve()
        hcu[chosen_airport_name] = [
            sum(
                [
                    df.loc[airport_name, chosen_input] * airport_lambda.varValue
                    for airport_name, airport_lambda in lambdas.items()
                ]
            )
            for chosen_input in ["i1", "i2", "i3", "i4"]
        ]
    return pd.DataFrame.from_dict(hcu, orient="index", columns=["i1", "i2", "i3", "i4"])


def calculate_cross_efficiencies(
    df: pd.DataFrame, efficiencies: Dict[str, float]
) -> pd.DataFrame:
    airports: List[str] = df.index.tolist()
    i1 = LpVariable("i1", lowBound=0, cat="Continuous")
    i2 = LpVariable("i2", lowBound=0, cat="Continuous")
    i3 = LpVariable("i3", lowBound=0, cat="Continuous")
    i4 = LpVariable("i4", lowBound=0, cat="Continuous")
    o1 = LpVariable("o1", lowBound=0, cat="Continuous")
    o2 = LpVariable("o2", lowBound=0, cat="Continuous")
    cross_efficiencies: Dict[str, List[float]] = {}
    for chosen_airport_name in airports:
        problem = LpProblem("problem", LpMaximize)
        airport: pd.Series = df.loc[chosen_airport_name]
        # Objective Function
        problem += (
            df.loc[:, "o1"].drop(chosen_airport_name).sum() * o1
            + df.loc[:, "o2"].drop(chosen_airport_name).sum() * o2,
            "Objective Function",
        )
        # Constraints
        problem += (
            df.loc[:, "i1"].drop(chosen_airport_name).sum() * i1
            + df.loc[:, "i2"].drop(chosen_airport_name).sum() * i2
            + df.loc[:, "i3"].drop(chosen_airport_name).sum() * i3
            + df.loc[:, "i4"].drop(chosen_airport_name).sum() * i4
            == 1,
            "airport Constraint",
        )
        airports_within = airports.copy()
        airports_within.remove(chosen_airport_name)
        for airport_name in airports_within:
            problem += (
                df.loc[airport_name, "o1"] * o1 + df.loc[airport_name, "o2"] * o2
                <= airport["i1"] * i1
                + airport["i2"] * i2
                + airport["i3"] * i3
                + airport["i4"] * i4,
                f"{airport_name} Constraint",
            )
        problem += (
            airport["o1"] * o1 + airport["o2"] * o2
            == efficiencies[chosen_airport_name]
            * (
                airport["i1"] * i1
                + airport["i2"] * i2
                + airport["i3"] * i3
                + airport["i4"] * i4
            ),
            f"{chosen_airport_name} Constraint",
        )
        # Solver
        # print("Current Status: ", LpStatus[problem.status])
        problem.solve()
        cross_efficiencies[chosen_airport_name] = [
            (
                df.loc[chosen_airport_name2, "o1"] * o1.varValue
                + df.loc[chosen_airport_name2, "o2"] * o2.varValue
            )
            / (
                df.loc[chosen_airport_name2, "i1"] * i1.varValue
                + df.loc[chosen_airport_name2, "i2"] * i2.varValue
                + df.loc[chosen_airport_name2, "i3"] * i3.varValue
                + df.loc[chosen_airport_name2, "i4"] * i4.varValue
            )
            for chosen_airport_name2 in airports
        ]
    return pd.DataFrame.from_dict(cross_efficiencies, orient="index", columns=airports)


def calculate_dist(df: pd.DataFrame) -> pd.DataFrame:
    airports: List[str] = df.index.tolist()
    i1 = LpVariable("i1", lowBound=0, cat="Continuous")
    i2 = LpVariable("i2", lowBound=0, cat="Continuous")
    i3 = LpVariable("i3", lowBound=0, cat="Continuous")
    i4 = LpVariable("i4", lowBound=0, cat="Continuous")
    o1 = LpVariable("o1", lowBound=0, cat="Continuous")
    o2 = LpVariable("o2", lowBound=0, cat="Continuous")
    b: Dict[str, LpVariable] = {
        airport: LpVariable(airport, lowBound=0, upBound=1, cat="Integer")
        for airport in airports
    }
    dist_weights: Dict[str, List[float]] = {}
    for chosen_airport_name in airports:
        problem = LpProblem("problem", LpMinimize)
        airport: pd.Series = df.loc[chosen_airport_name]
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
        for airport_name in airports:
            problem += (
                df.loc[airport_name, "o1"] * o1 + df.loc[airport_name, "o2"] * o2
                >= df.loc[airport_name, "i1"] * i1
                + df.loc[airport_name, "i2"] * i2
                + df.loc[airport_name, "i3"] * i3
                + df.loc[airport_name, "i4"] * i4
                - 9999 * (1 - b.get(airport_name)),
                f"{airport_name} Function",
            )
        problem += sum(b.values()) >= 1
        problem.solve()
        # print("Current Status: ", LpStatus[problem.status])
    return pd.DataFrame()


def main():
    df_input: pd.DataFrame = read_csv("inputs.csv")
    df_output: pd.DataFrame = read_csv("outputs.csv")
    df: pd.DataFrame = pd.concat([df_input, df_output], axis=1)
    efficiencies: Dict[str, float] = calculate_efficiencies(df)
    super_efficiencies: Dict[str, float] = calculate_efficiencies(df, True)
    hcu_df = calculate_hcu(df)
    cross_efficiencies_df = calculate_cross_efficiencies(df, efficiencies)
    calculate_dist(df)
    # print(efficiencies)
    # print(super_efficiencies)
    # print(hcu_df)
    # print(df.loc[:, "i1":"i4"] - hcu_df)
    # with pd.option_context(
    #     "display.max_rows", None, "display.max_columns", None
    # ):
    #     print(cross_efficiencies_df.round(3))
    # print(cross_efficiencies_df.mean(axis=0).round(3))


if __name__ == "__main__":
    main()
