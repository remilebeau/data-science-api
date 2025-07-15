from fastapi import APIRouter, HTTPException
from ortools.linear_solver import pywraplp
from pydantic import BaseModel


class Constraints(BaseModel):
    monReq: int
    tueReq: int
    wedReq: int
    thuReq: int
    friReq: int
    satReq: int
    sunReq: int


router = APIRouter(
    prefix="/api/optimizations",
    tags=["optimizations"],
)


# @DESC optimization model for minimizing staffing
# @route POST /api/optimizations/staffing
# @access public
@router.post(
    "/staffing",
    summary="Optimize staffing schedule",
    response_description="Optimal staffing configuration",
)
def optimization_staffing(constraints: Constraints):
    """
    Optimize weekly staffing using linear programming.

    Minimizes total staff needed while ensuring daily worker requirements are met.
    Each worker is assigned to a 5-day shift (e.g., Mon-Fri, Tue-Sat, etc.).

    ### Request Body
    - monReq to sunReq: Required workers per day.

    ### Response (on success)
    - minStaff: Total staff needed
    - x1-x7: Workers assigned to each 5-day shift
    - monAva-sunAva: Workers available each day
    - monSlack-sunSlack: Surplus workers per day
    - totalSlack: Total surplus
    """
    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # decision variables
    x1 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x1")
    x2 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x2")
    x3 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x3")
    x4 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x4")
    x5 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x5")
    x6 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x6")
    x7 = solver.IntVar(lb=0, ub=solver.Infinity(), name="x7")
    # objective function
    min_staff = x1 + x2 + x3 + x4 + x5 + x6 + x7
    # constraints
    # LHS
    monAva = x1 + x4 + x5 + x6 + x7
    tueAva = x1 + x2 + x5 + x6 + x7
    wedAva = x1 + x2 + x3 + x6 + x7
    thuAva = x1 + x2 + x3 + x4 + x7
    friAva = x1 + x2 + x3 + x4 + x5
    satAva = x2 + x3 + x4 + x5 + x6
    sunAva = x3 + x4 + x5 + x6 + x7
    # add constraints
    solver.Add(monAva >= constraints.monReq)
    solver.Add(tueAva >= constraints.tueReq)
    solver.Add(wedAva >= constraints.wedReq)
    solver.Add(thuAva >= constraints.thuReq)
    solver.Add(friAva >= constraints.friReq)
    solver.Add(satAva >= constraints.satReq)
    solver.Add(sunAva >= constraints.sunReq)
    # solve
    solver.Minimize(min_staff)
    status = solver.Solve()
    # calculate slack for each constraint
    monSlack = monAva.solution_value() - constraints.monReq
    tueSlack = tueAva.solution_value() - constraints.tueReq
    wedSlack = wedAva.solution_value() - constraints.wedReq
    thuSlack = thuAva.solution_value() - constraints.thuReq
    friSlack = friAva.solution_value() - constraints.friReq
    satSlack = satAva.solution_value() - constraints.satReq
    sunSlack = sunAva.solution_value() - constraints.sunReq
    totalSlack = (
        monSlack + tueSlack + wedSlack + thuSlack + friSlack + satSlack + sunSlack
    )
    # print results
    if status == pywraplp.Solver.OPTIMAL:
        return {
            "minStaff": solver.Objective().Value(),
            "x1": x1.solution_value(),
            "x2": x2.solution_value(),
            "x3": x3.solution_value(),
            "x4": x4.solution_value(),
            "x5": x5.solution_value(),
            "x6": x6.solution_value(),
            "x7": x7.solution_value(),
            "monAva": monAva.solution_value(),
            "tueAva": tueAva.solution_value(),
            "wedAva": wedAva.solution_value(),
            "thuAva": thuAva.solution_value(),
            "friAva": friAva.solution_value(),
            "satAva": satAva.solution_value(),
            "sunAva": sunAva.solution_value(),
            "monReq": constraints.monReq,
            "tueReq": constraints.tueReq,
            "wedReq": constraints.wedReq,
            "thuReq": constraints.thuReq,
            "friReq": constraints.friReq,
            "satReq": constraints.satReq,
            "sunReq": constraints.sunReq,
            "monSlack": monSlack,
            "tueSlack": tueSlack,
            "wedSlack": wedSlack,
            "thuSlack": thuSlack,
            "friSlack": friSlack,
            "satSlack": satSlack,
            "sunSlack": sunSlack,
            "totalSlack": totalSlack,
        }

    else:
        raise HTTPException(status_code=400, detail="No solution found")
