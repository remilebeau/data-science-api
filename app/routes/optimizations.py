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
    x1Max: int
    x2Max: int
    x3Max: int
    x4Max: int
    x5Max: int
    x6Max: int
    x7Max: int


router = APIRouter(
    prefix="/api/optimizations",
    tags=["optimizations"],
)


# @DESC optimization model for minimizing staffing
# @route POST /api/optimizations/staffing
# @access public
@router.post("/staffing")
def optimization_staffing(constraints: Constraints):

    # create solver
    solver = pywraplp.Solver.CreateSolver("SCIP")

    # define upper bounds, if provided
    x1Ub = constraints.x1Max if constraints.x1Max >= 0 else solver.Infinity()
    x2Ub = constraints.x2Max if constraints.x2Max >= 0 else solver.Infinity()
    x3Ub = constraints.x3Max if constraints.x3Max >= 0 else solver.Infinity()
    x4Ub = constraints.x4Max if constraints.x4Max >= 0 else solver.Infinity()
    x5Ub = constraints.x5Max if constraints.x5Max >= 0 else solver.Infinity()
    x6Ub = constraints.x6Max if constraints.x6Max >= 0 else solver.Infinity()
    x7Ub = constraints.x7Max if constraints.x7Max >= 0 else solver.Infinity()

    # decision variables
    x1 = solver.IntVar(lb=0, ub=x1Ub, name="x1")
    x2 = solver.IntVar(lb=0, ub=x2Ub, name="x2")
    x3 = solver.IntVar(lb=0, ub=x3Ub, name="x3")
    x4 = solver.IntVar(lb=0, ub=x4Ub, name="x4")
    x5 = solver.IntVar(lb=0, ub=x5Ub, name="x5")
    x6 = solver.IntVar(lb=0, ub=x6Ub, name="x6")
    x7 = solver.IntVar(lb=0, ub=x7Ub, name="x7")
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
    # calculate slack for each constraint
    monSlack = monAva.solution_value() - monReq
    tueSlack = tueAva.solution_value() - tueReq
    wedSlack = wedAva.solution_value() - wedReq
    thuSlack = thuAva.solution_value() - thuReq
    friSlack = friAva.solution_value() - friReq
    satSlack = satAva.solution_value() - satReq
    sunSlack = sunAva.solution_value() - sunReq
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
