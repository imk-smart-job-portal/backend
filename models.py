from pydantic import BaseModel, Field
from typing import Optional


class JobCreate(BaseModel):
    company_id: int = Field(..., title="ID Perusahaan", description="ID perusahaan yang menawarkan pekerjaan")
    category_id: Optional[int] = Field(None, title="ID Kategori", description="Kategori pekerjaan yang relevan")
    title: str = Field(..., title="Judul Pekerjaan", description="Judul pekerjaan yang ditawarkan")
    description: str = Field(..., title="Deskripsi Pekerjaan", description="Deskripsi pekerjaan secara detail")
    experience_level: Optional[str] = Field(None, title="Tingkat Pengalaman", description="Tingkat pengalaman yang diperlukan (misal: Pemula, Menengah, Lanjutan)")
    education_level: Optional[str] = Field(None, title="Tingkat Pendidikan", description="Tingkat pendidikan yang diperlukan (misal: SMA, Sarjana, Magister)")
    career_level: Optional[str] = Field(None, title="Tingkat Karier", description="Tingkat karier yang diinginkan (misal: Junior, Senior, Lead)")
    employment_type: Optional[str] = Field(None, title="Jenis Pekerjaan", description="Jenis pekerjaan yang ditawarkan (misal: Penuh Waktu, Paruh Waktu, Kontrak)")
    required_skills: Optional[str] = Field(None, title="Keahlian yang Diperlukan", description="Daftar keterampilan yang diperlukan untuk pekerjaan ini")

class JobUpdate(BaseModel):
    category_id: Optional[int] = Field(None, title="ID Kategori", description="Kategori pekerjaan yang relevan")
    title: Optional[str] = Field(None, title="Judul Pekerjaan", description="Judul pekerjaan yang ditawarkan")
    description: Optional[str] = Field(None, title="Deskripsi Pekerjaan", description="Deskripsi pekerjaan secara detail")
    experience_level: Optional[str] = Field(None, title="Tingkat Pengalaman", description="Tingkat pengalaman yang diperlukan")
    education_level: Optional[str] = Field(None, title="Tingkat Pendidikan", description="Tingkat pendidikan yang diperlukan")
    career_level: Optional[str] = Field(None, title="Tingkat Karier", description="Tingkat karier yang diinginkan")
    employment_type: Optional[str] = Field(None, title="Jenis Pekerjaan", description="Jenis pekerjaan yang ditawarkan")
    required_skills: Optional[str] = Field(None, title="Keahlian yang Diperlukan", description="Daftar keterampilan yang diperlukan untuk pekerjaan ini")

class JobResponse(BaseModel):
    id: int
    company_id: int
    category_id: Optional[int]
    title: str
    description: str
    experience_level: Optional[str]
    education_level: Optional[str]
    career_level: Optional[str]
    employment_type: Optional[str]
    required_skills: Optional[str]

    class Config:
        orm_mode = True
