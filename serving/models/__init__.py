from pydantic import BaseModel, Field

class IrisInput(BaseModel):
    SepalLengthCm: float = Field(..., gt=0, description="Sepal length in centimeters")
    SepalWidthCm: float = Field(..., gt=0, description="Sepal width in centimeters")
    PetalLengthCm: float = Field(..., gt=0, description="Petal length in centimeters")
    PetalWidthCm: float = Field(..., gt=0, description="Petal width in centimeters")

class IrisPrediction(BaseModel):
    Species: str = Field(..., description="Predicted iris species")

class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    model_prod_loaded: bool = Field(..., description="Whether the model prod is loaded")
    model_shadow_loaded: bool = Field(..., description="Whether the model shadow is loaded")
    model_prod_name: str = Field(..., description="Production model name")
    model_prod_version: str = Field(..., description="Production model version")
    model_shadow_name: str = Field(..., description="Shadow model name")
    model_shadow_version: str = Field(..., description="Shadow model version") 