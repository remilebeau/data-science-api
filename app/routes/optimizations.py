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
    x1Max: int | None = None
    x2Max: int | None = None
    x3Max: int | None = None
    x4Max: int | None = None
    x5Max: int | None = None
    x6Max: int | None = None
    x7Max: int | None = None


router = APIRouter(
    prefix="/api/optimizations",
    tags=["optimizations"],
    responses={404: {"description": "Not found"}},
)


# @DESC optimization model for minimizing staffing
# @route POST /api/optimizations/staffing
# @access public
@router.post("/staffing")
def optimization_staffing(constraints: Constraints):
    """
    PARAMS:\n
    monReq: number of Monday staff required\n
    tueReq: number of Tuesday staff required\n
    wedReq: number of Wednesday staff required\n
    thuReq: number of Thursday staff required\n
    friReq: number of Friday staff required\n
    satReq: number of Saturday staff required\n
    sunReq: number of Sunday staff required\n

    RETURNS:\n
    x1 = number of Monday to Friday staff\n
    x2 = number of Tuesday to Saturday staff\n
    x3 = number of Wednesday to Sunday staff\n
    x4 = number of Monday to Saturday staff\n
    x5 = number of Tuesday to Sunday staff\n
    x6 = number of Wednesday to Saturday staff\n
    x7 = number of Thursday to Sunday staff\n
    """

    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # decision variables
    x1 = solver.IntVar(lb=0, ub=constraints.x1Max or solver.Infinity(), name="x1")
    x2 = solver.IntVar(lb=0, ub=constraints.x2Max or solver.Infinity(), name="x2")
    x3 = solver.IntVar(lb=0, ub=constraints.x3Max or solver.Infinity(), name="x3")
    x4 = solver.IntVar(lb=0, ub=constraints.x4Max or solver.Infinity(), name="x4")
    x5 = solver.IntVar(lb=0, ub=constraints.x5Max or solver.Infinity(), name="x5")
    x6 = solver.IntVar(lb=0, ub=constraints.x6Max or solver.Infinity(), name="x6")
    x7 = solver.IntVar(lb=0, ub=constraints.x7Max or solver.Infinity(), name="x7")
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
    # RHS
    monReq = constraints.monReq
    tueReq = constraints.tueReq
    wedReq = constraints.wedReq
    thuReq = constraints.thuReq
    friReq = constraints.friReq
    satReq = constraints.satReq
    sunReq = constraints.sunReq
    # add constraints
    solver.Add(monAva >= monReq)
    solver.Add(tueAva >= tueReq)
    solver.Add(wedAva >= wedReq)
    solver.Add(thuAva >= thuReq)
    solver.Add(friAva >= friReq)
    solver.Add(satAva >= satReq)
    solver.Add(sunAva >= sunReq)
    # solve
    solver.Minimize(min_staff)
    status = solver.Solve()
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
        }

    else:
        raise HTTPException(status_code=404, detail="No solution found")
