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
@router.post("/staffing")
def optimization_staffing(constraints: Constraints):
    """
    X1 = number of Mon to Fri workers\n
    X2 = number of Tue to Sat workers\n
    X3 = number of Wed to Sun workers\n
    X4 = number of Thu to Mon workers\n
    X5 = number of Fri to Tue workers\n
    X6 = number of Sat to Wed workers\n
    X7 = number of Sun to Thu workers\n
    Minimize X1 + X2 + X3 + X4 + X5 + X6 + X7\n
    s.t.\n
    Mon staff available >= Mon staff required\n
    Tue staff available >= Tue staff required\n
    Wed staff available >= Wed staff required\n
    Thu staff available >= Thu staff required\n
    Fri staff available >= Fri staff required\n
    Sat staff available >= Sat staff required\n
    Sun staff available >= Sun staff required\n
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
    totalSlack = monSlack + tueSlack + wedSlack + thuSlack + friSlack + satSlack + sunSlack
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
