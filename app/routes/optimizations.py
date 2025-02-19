from fastapi import APIRouter, HTTPException
from ortools.linear_solver import pywraplp
from pydantic import BaseModel


class StaffingRequirements(BaseModel):
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
    responses={404: {"description": "Not found"}},
)


# @DESC optimization model for minimizing staffing
# @route GET /api/optimizations/staffing
# @access public
@router.get("/staffing")
def optimization_staffing(requirements: StaffingRequirements):

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
    monReq = requirements.monReq
    tueReq = requirements.tueReq
    wedReq = requirements.wedReq
    thuReq = requirements.thuReq
    friReq = requirements.friReq
    satReq = requirements.satReq
    sunReq = requirements.sunReq
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
