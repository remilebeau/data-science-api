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

    monday = Monday staff constraint\n
    tuesday = Tuesday staff constraint\n
    wednesday = Wednesday staff constraint\n
    thursday = Thursday staff constraint\n
    friday = Friday staff constraint\n
    saturday = Saturday staff constraint\n
    sunday = Sunday staff constraint\n

    RESULTS:

    ObjFuncVal = minimum number of staff that meets staffing requirements\n
    xMondayFriday = number of Monday to Friday staff\n
    xTuesdaySaturday = number of Tuesday to Saturday staff\n
    xWednesdaySunday = number of Wednesday to Sunday staff\n
    xThursdayMonday = number of Thursday to Monday staff\n
    xFridayTuesday = number of Friday to Tuesday staff\n
    xSaturdayWednesday = number of Saturday to Wednesday staff\n
    xSundayThursday = number of Sunday to Thursday staff\n
    """

    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # decision variables
    xMondayFriday = solver.IntVar(0, solver.Infinity(), "xMondayFriday")
    xTuesdaySaturday = solver.IntVar(0, solver.Infinity(), "xTuesdaySaturday")
    xWednesdaySunday = solver.IntVar(0, solver.Infinity(), "xWednesdaySunday")
    xThursdayMonday = solver.IntVar(0, solver.Infinity(), "xThursdayMonday")
    xFridayTuesday = solver.IntVar(0, solver.Infinity(), "xFridayTuesday")
    xSaturdayWednesday = solver.IntVar(0, solver.Infinity(), "xSaturdayWednesday")
    xSundayThursday = solver.IntVar(0, solver.Infinity(), "xSundayThursday")
    # objective function
    obj_func = (
        xMondayFriday
        + xTuesdaySaturday
        + xWednesdaySunday
        + xThursdayMonday
        + xFridayTuesday
        + xSaturdayWednesday
        + xSundayThursday
    )
    # constraints
    monday_staff = (
        xMondayFriday
        + xThursdayMonday
        + xFridayTuesday
        + xSaturdayWednesday
        + xSundayThursday
    )
    tuesday_staff = (
        xMondayFriday
        + xTuesdaySaturday
        + xFridayTuesday
        + xSaturdayWednesday
        + xSundayThursday
    )
    wednesday_staff = (
        xMondayFriday
        + xTuesdaySaturday
        + xWednesdaySunday
        + xSaturdayWednesday
        + xSundayThursday
    )
    thursday_staff = (
        xMondayFriday
        + xTuesdaySaturday
        + xWednesdaySunday
        + xThursdayMonday
        + xSundayThursday
    )
    friday_staff = (
        xMondayFriday
        + xTuesdaySaturday
        + xWednesdaySunday
        + xThursdayMonday
        + xFridayTuesday
    )
    saturday_staff = (
        xTuesdaySaturday
        + xWednesdaySunday
        + xThursdayMonday
        + xFridayTuesday
        + xSaturdayWednesday
    )
    sunday_staff = (
        xWednesdaySunday
        + xThursdayMonday
        + xFridayTuesday
        + xSaturdayWednesday
        + xSundayThursday
    )
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
            "xMondayFriday": xMondayFriday.solution_value(),
            "xTuesdaySaturday": xTuesdaySaturday.solution_value(),
            "xWednesdaySunday": xWednesdaySunday.solution_value(),
            "xThursdayMonday": xThursdayMonday.solution_value(),
            "xFridayTuesday": xFridayTuesday.solution_value(),
            "xSaturdayWednesday": xSaturdayWednesday.solution_value(),
            "xSundayThursday": xSundayThursday.solution_value(),
            "mondayStaff": monday_staff.solution_value(),
            "tuesdayStaff": tuesday_staff.solution_value(),
            "wednesdayStaff": wednesday_staff.solution_value(),
            "thursdayStaff": thursday_staff.solution_value(),
            "fridayStaff": friday_staff.solution_value(),
            "saturdayStaff": saturday_staff.solution_value(),
            "sundayStaff": sunday_staff.solution_value(),
        }

    else:
        raise HTTPException(status_code=404, detail="No solution found")
