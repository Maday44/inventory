import React, { useEffect, useState } from "react";
import axios from "axios";

// hard code number of item shown
const MAX_ITEMS = 6



const OtherItemsPad = () => {
  const [otherItems, setOtherItems] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/Other%20items/")
      .then((response) => {
        setOtherItems(response.data.results || response.data || []);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Failed to fetch food items:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p className="text-center mt-5">Loading...</p>;

  return (
    <div className="container py-5">
      <h2 className="text-center mb-5 fw-bold">Other Items</h2>

      {/* Grid container */}
      <div
        className="food-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(250px, 1fr))",
          gap: "20px",
        }}
      >
   
        
        {otherItems.slice(0, MAX_ITEMS).map((item) => (
          <div
            key={item.id}
            className="card h-100 border-0 shadow-sm rounded-4"
            style={{
              aspectRatio: "1 / 1", // makes each card a square
              display: "flex",
              flexDirection: "column",
              transition: "transform 0.2s ease, box-shadow 0.2s ease",
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = "translateY(-6px)";
              e.currentTarget.style.boxShadow = "0 6px 20px rgba(0,0,0,0.15)";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = "translateY(0)";
              e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
            }}
          >
            <img
              src={item.image}
              alt={item.title}
              style={{
                height: "50%",
                width: "100%",
                objectFit: "cover",
                borderTopLeftRadius: "1rem",
                borderTopRightRadius: "1rem",
              }}
            />
            <div
              className="card-body d-flex flex-column justify-content-between"
              style={{ flex: 1 }}
            >
              <div>
                <h5 className="card-title fw-semibold mb-2">{item.title}</h5>
                <p className="card-text text-muted mb-1">
                  <strong>Brand:</strong> {item.brand || "N/A"}
                </p>
                <p className="card-text text-muted mb-1">
                  <strong>Quantity:</strong> {item.quantity}
                </p>
                
              </div>
              <div className="mt-auto text-center">
                <button className="btn btn-outline-primary btn-sm rounded-pill px-4">
                  View Details
                </button>
              </div>
            </div>
          </div>
        ))}
        {otherItems.length === 0 && (
          <p className="text-center">No food items found.</p>
        )}
      </div>
    </div>
  );
};

export default OtherItemsPad;