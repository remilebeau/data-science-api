from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes.distributions import router as distributions_router
from .routes.simulations import router as simulations_router

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

app.include_router(distributions_router)
app.include_router(simulations_router)
