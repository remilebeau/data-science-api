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
@router.get("/staffing")
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
    optimization model to minimize staffing

    PARAMS:

    monday = number of employees required every Monday

    RESULTS:

    ObjFuncVal = minimum number of employees to satisfy staffing requirements

    xMonday = number of employees whose workweek begins on Monday (i.e. Monday to Friday)



    the same pattern applies to all seven days of the week
    """

    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # decision variables
    xMonday = solver.IntVar(0, solver.Infinity(), "xMonday")
    xTuesday = solver.IntVar(0, solver.Infinity(), "xTuesday")
    xWednesday = solver.IntVar(0, solver.Infinity(), "xWednesday")
    xThursday = solver.IntVar(0, solver.Infinity(), "xThursday")
    xFriday = solver.IntVar(0, solver.Infinity(), "xFriday")
    xSaturday = solver.IntVar(0, solver.Infinity(), "xSaturday")
    xSunday = solver.IntVar(0, solver.Infinity(), "xSunday")
    # constraints
    solver.Add(xMonday + xThursday + xFriday + xSaturday + xSunday >= monday)
    solver.Add(xMonday + xTuesday + xFriday + xSaturday + xSunday >= tuesday)
    solver.Add(xMonday + xTuesday + xWednesday + xSaturday + xSunday >= wednesday)
    solver.Add(xMonday + xTuesday + xWednesday + xThursday + xSunday >= thursday)
    solver.Add(xMonday + xTuesday + xWednesday + xThursday + xFriday >= friday)
    solver.Add(xTuesday + xWednesday + xThursday + xFriday + xSaturday >= saturday)
    solver.Add(xWednesday + xThursday + xFriday + xSaturday + xSunday >= sunday)
    # solve
    solver.Minimize(
        xMonday + xTuesday + xWednesday + xThursday + xFriday + xSaturday + xSunday
    )
    status = solver.Solve()
    # print results
    if status == pywraplp.Solver.OPTIMAL:
        return {
            "objFuncVal": solver.Objective().Value(),
            "xMonday": xMonday.solution_value(),
            "xTuesday": xTuesday.solution_value(),
            "xWednesday": xWednesday.solution_value(),
            "xThursday": xThursday.solution_value(),
            "xFriday": xFriday.solution_value(),
            "xSaturday": xSaturday.solution_value(),
            "xSunday": xSunday.solution_value(),
        }

    else:
        raise HTTPException(status_code=404, detail="No solution found")
