"""
Quick start script to run the API locally without geospatial dependencies
"""
import uvicorn

if __name__ == "__main__":
    print("=" * 60)
    print("PuneRakshak API - Starting in minimal mode")
    print("=" * 60)
    print("\nAPI will be available at: http://localhost:8000")
    print("API docs at: http://localhost:8000/docs")
    print("\nNote: Grid generation requires additional geospatial libraries.")
    print("The API endpoints will work once you populate the database.")
    print("=" * 60)
    print()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
