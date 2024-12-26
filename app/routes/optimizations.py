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

    monday = number of staff required every Monday\n
    tuesday = number of staff required every Tuesday\n
    wednesday = number of staff required every Wednesday\n
    thursday = number of staff required every Thursday\n
    friday = number of staff required every Friday\n
    saturday = number of staff required every Saturday\n
    sunday = number of staff required every Sunday\n

    RESULTS:

    ObjFuncVal = minimum number of staff to satisfy staffing requirements. Equal to the sum of xMonday...xSunday\n
    xMonday = number of staff whose workweek begins on Monday (Monday to Friday)\n
    xTuesday = number of staff whose workweek begins on Tuesday (Tuesday to Saturday)\n
    xWednesday = number of staff whose workweek begins on Wednesday (Wednesday to Sunday)\n
    xThursday = number of staff whose workweek begins on Thursday (Thursday to Monday)\n
    xFriday = number of staff whose workweek begins on Friday (Friday to Tuesday)\n
    xSaturday = number of staff whose workweek begins on Saturday (Saturday to Wednesday)\n
    xSunday = number of staff whose workweek begins on Sunday (Sunday to Thursday)\n
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
    # objective function
    obj_func = (
        xMonday + xTuesday + xWednesday + xThursday + xFriday + xSaturday + xSunday
    )
    # constraints
    monday_staff = xMonday + xThursday + xFriday + xSaturday + xSunday
    tuesday_staff = xMonday + xTuesday + xFriday + xSaturday + xSunday
    wednesday_staff = xMonday + xTuesday + xWednesday + xSaturday + xSunday
    thursday_staff = xMonday + xTuesday + xWednesday + xThursday + xSunday
    friday_staff = xMonday + xTuesday + xWednesday + xThursday + xFriday
    saturday_staff = xTuesday + xWednesday + xThursday + xFriday + xSaturday
    sunday_staff = xWednesday + xThursday + xFriday + xSaturday + xSunday
    solver.Add(monday_staff >= monday)
    solver.Add(tuesday_staff >= tuesday)
    solver.Add(wednesday_staff >= wednesday)
    solver.Add(thursday_staff >= thursday)
    solver.Add(friday_staff >= friday)
    solver.Add(saturday_staff >= saturday)
    solver.Add(sunday_staff >= sunday)
    # solve
    solver.Minimize(obj_func)
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
