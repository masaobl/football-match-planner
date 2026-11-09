
from pydantic import BaseModel, ConfigDict, Field


class MatchAdvice(BaseModel):
    # Ne dovolimo dodatnih polj v JSON odgovoru.
    model_config = ConfigDict(extra="forbid")

    povzetek: str = Field(
        description="Kratek povzetek priporočil za obisk tekme"
    )

    priporoceni_predmeti: list[str] = Field(
        description="Seznam predmetov, ki jih je priporočljivo vzeti na tekmo"
    )

    nasveti: list[str] = Field(
        description="Praktični nasveti za obisk nogometne tekme"
    )
