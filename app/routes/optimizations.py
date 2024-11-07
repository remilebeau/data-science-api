from fastapi import APIRouter, HTTPException
from ortools.linear_solver import pywraplp

router = APIRouter(
    prefix="/api/optimizations",
    tags=["optimizations"],
    responses={404: {"description": "Not found"}},
)


# @DESC optimization model for minimizing staffing
# @route GET /api/optimizations/staffing
# @access public
def optimization_staffing(
    monday: int,
    tuesday: int,
    wednesday: int,
    thursday: int,
    friday: int,
    saturday: int,
    sunday: int,
):
    """
    minimize x1+x2+x3+x4+x5+x6+x7
    s.t.
    x1+x4+x5+x6+x7 >= monday
    x1+x2+x5+x6+x7 >= tuesday
    x1+x2+x3+x6+x7 >= wednesday
    x1+x2+x3+x4+x7 >= thursday
    x1+x2+x3+x4+x5 >= friday
    x2+x3+x4+x5+x6 >= saturday
    x3+x4+x5+x6+x7 >= sunday
    """

    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # decision variables
    x1 = solver.IntVar(0, solver.Infinity(), "x1")
    x2 = solver.IntVar(0, solver.Infinity(), "x2")
    x3 = solver.IntVar(0, solver.Infinity(), "x3")
    x4 = solver.IntVar(0, solver.Infinity(), "x4")
    x5 = solver.IntVar(0, solver.Infinity(), "x5")
    x6 = solver.IntVar(0, solver.Infinity(), "x6")
    x7 = solver.IntVar(0, solver.Infinity(), "x7")
    # constraints
    solver.Add(x1 + x4 + x5 + x6 + x7 >= monday)
    solver.Add(x1 + x2 + x5 + x6 + x7 >= tuesday)
    solver.Add(x1 + x2 + x3 + x6 + x7 >= wednesday)
    solver.Add(x1 + x2 + x3 + x4 + x7 >= thursday)
    solver.Add(x1 + x2 + x3 + x4 + x5 >= friday)
    solver.Add(x2 + x3 + x4 + x5 + x6 >= saturday)
    solver.Add(x3 + x4 + x5 + x6 + x7 >= sunday)
    # solve
    solver.Minimize(x1 + x2 + x3 + x4 + x5 + x6 + x7)
    status = solver.Solve()
    # print results
    if status == pywraplp.Solver.OPTIMAL:
        return {
            "objFuncVal": solver.Objective().Value(),
            "x1": x1.solution_value(),
            "x2": x2.solution_value(),
            "x3": x3.solution_value(),
            "x4": x4.solution_value(),
            "x5": x5.solution_value(),
            "x6": x6.solution_value(),
            "x7": x7.solution_value(),
        }

    else:
        raise HTTPException(status_code=404, detail="No solution found")
