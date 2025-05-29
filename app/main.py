from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .routes import optimizations, simulations

app = FastAPI()


# configure CORS
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routes
app.include_router(simulations.router)
app.include_router(optimizations.router)

# root page


@app.get("/", include_in_schema=False)
def custom_homepage():
    html_content = """
    <html>
        <head><title>Production Simulation API</title></head>
        <body>
            <h1>Welcome to the Production Simulation and Staffing Optimization API</h1>
            <p>Developed by remilebeau</p>
            <p>Visit <a href='/docs'>Swagger UI</a> for interactive documentation.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)
