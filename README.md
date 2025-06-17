# 📊 Data Science API – Monte Carlo Simulation & Workforce Optimization

A production-ready API built with **FastAPI** for solving real-world business problems using **simulation modeling** and **linear optimization**. This project demonstrates applied data science techniques deployed as scalable APIs, with a focus on decision-making under uncertainty and operational efficiency.

## 🔍 Project Overview

This repo includes two endpoints:

1. **Monte Carlo Production Simulation**  
   Simulates 1,000 demand scenarios using a **truncated normal distribution** to analyze expected profit, volatility, Sharpe ratio, and risk percentiles. Useful for production planning under demand uncertainty.

2. **Workforce Optimization**  
   Uses **linear programming** (via Google OR-Tools) to assign staff to rotating shifts across a 7-day schedule, minimizing total headcount while meeting daily coverage requirements.

Both endpoints are **deployed with FastAPI** and include **parameter validation**, **Pydantic models**, and **business-focused outputs**.

---

## 🛠️ Tech Stack

- **Python 3.11**
- **FastAPI** – lightweight, fast web framework
- **OR-Tools** – Google’s optimization toolkit
- **NumPy** – numerical computing
- **Pydantic** – data validation and serialization
- **Uvicorn** – ASGI server for local development

---

## 🚀 Live Demos

- 🔗 **Monte Carlo Simulation**  
  [https://remilebeau-ds.vercel.app/simulation](https://remilebeau-ds.vercel.app/simulation)

- 🔗 **Workforce Optimization**  
  [https://remilebeau-ds.vercel.app/optimization](https://remilebeau-ds.vercel.app/optimization)

---
