import numpy as np
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from scipy.optimize import minimize

router = APIRouter(
    prefix="/api/optimizations",
    tags=["optimizations"],
)

class StaffingInputs(BaseModel):
    wage: float
    fixed_overhead: float
    demand_intensity: float  # Scalar for the workload
    min_service_level: float  # e.g., 0.85 (85%)
    current_headcount: float

# --- CORE MATHEMATICAL MODELS ---

def calculate_service_level(headcount: float, intensity: float) -> float:
    """
    Models service level using a modified Erlang-C logic or exponential decay.
    As headcount increases relative to intensity, service level approaches 1.0 (100%).
    """
    if headcount <= 0: 
        return 0.0
    # A standard saturation curve: 1 - e^(-k * (headcount/intensity))
    return 1 - np.exp(-0.8 * (headcount / (intensity / 10)))

def cost_objective(headcount: float, wage: float, fixed: float) -> float:
    """Total labor cost function."""
    return (headcount * wage) + fixed

# --- ENDPOINTS ---

@router.post("/staffing-plan")
def get_staffing_plan(inputs: StaffingInputs):
    # 1. Mathematical Optimization (The "Plan")
    cons = ({
        'type': 'ineq', 
        'fun': lambda x: calculate_service_level(x[0], inputs.demand_intensity) - inputs.min_service_level
    })
    
    # Solve for optimal headcount
    res = minimize(lambda x: x[0], x0=[inputs.demand_intensity / 20], constraints=cons, bounds=[(0, None)])
    
    if not res.success:
        raise HTTPException(status_code=400, detail="Optimization failed")

    optimal_hc = float(res.x[0])
    optimized_cost = cost_objective(optimal_hc, inputs.wage, inputs.fixed_overhead)
    
    # 2. Current State (The "Actual")
    current_cost = cost_objective(inputs.current_headcount, inputs.wage, inputs.fixed_overhead)
    
    # 3. Variance Analysis Logic
    # If Current > Optimal = Overstaffed (Positive Savings Potential)
    # If Current < Optimal = Understaffed (Negative Savings / Risk)
    cost_variance = current_cost - optimized_cost
    
    # Status should be based on the headcount delta
    status_msg = "Overstaffed" if inputs.current_headcount > optimal_hc else "Understaffed"
    
    # Calculate Efficiency Gain (only if overstaffed, otherwise it's a 'service gap')
    efficiency_gain = (cost_variance / current_cost * 100) if current_cost > 0 else 0

    return {
        "plan": {
            "targetSLA": round(inputs.min_service_level * 100, 1),
            "requiredHeadcount": round(optimal_hc, 1),
            "totalCost": round(optimized_cost, 2),
            "headcountDelta": round(optimal_hc - inputs.current_headcount, 1) # Positive means hire, Negative means cut
        },
        "comparison": {
            "actualCost": round(current_cost, 2),
            "potentialSavings": round(cost_variance, 2),
            "efficiencyGain": round(efficiency_gain, 1),
            "status": status_msg
        }
    }


@router.post("/staffing")
def optimize_staffing(inputs: StaffingInputs):
    """
    Finds the MINIMUM headcount (and cost) required to hit a specific Service Level target.
    """
    # Constraint: service_level >= min_service_level
    # Rearranged for scipy (must be >= 0): calculate_service_level - min_service_level >= 0
    cons = ({
        'type': 'ineq', 
        'fun': lambda x: calculate_service_level(x[0], inputs.demand_intensity) - inputs.min_service_level
    })
    
    # Minimize headcount
    res = minimize(lambda x: x[0], x0=[10], constraints=cons, bounds=[(0, None)])

    if not res.success:
        raise HTTPException(status_code=400, detail="Optimization failed to converge")

    optimal_headcount = float(res.x[0])
    total_cost = cost_objective(optimal_headcount, inputs.wage, inputs.fixed_overhead)

    return {
        "optimalHeadcount": round(optimal_headcount, 2),
        "totalCost": round(total_cost, 2),
        "achievedServiceLevel": round(calculate_service_level(optimal_headcount, inputs.demand_intensity), 4)
    }

@router.post("/frontier")
def get_efficient_frontier(inputs: StaffingInputs):
    """
    Generates a range of optimal points showing the trade-off between Cost and Service Level.
    This provides the data for the shadcn/ui Line Chart.
    """
    # Generate targets from 70% to 99% service levels
    service_targets = np.linspace(0.70, 0.99, 15)

    for target in service_targets:
        cons = ({
            'type': 'ineq', 
            'fun': lambda x: calculate_service_level(x[0], inputs.demand_intensity) - target
        })
        
        res = minimize(lambda x: x[0], x0=[10], constraints=cons, bounds=[(0, None)])
        
        if res.success:
            headcount = float(res.x[0])
            cost = cost_objective(headcount, inputs.wage, inputs.fixed_overhead)
            
            return {
                 "serviceLevel": round(target * 100, 1),
                "minCost": round(cost, 2),
                # "Inefficiency" mock data to show gap on chart
                "currentSpend": round(cost * 1.15, 2) 
            }
        

    raise HTTPException(status_code=400, detail="Optimization failed to converge")