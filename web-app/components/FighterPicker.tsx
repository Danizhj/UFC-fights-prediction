"use client";
import React, { useState } from "react";

type Fighter = {
  name: string;
  nickname: string;
  division: string;
  rating: number;
  record: string;
};

export default function FighterPicker({
  initialList,
}: {
  initialList: Fighter[];
}) {
  const [selected, setSelected] = useState<string[]>([]);
  const [hovered, setHovered] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  function toggle(name: string) {
    setSelected((prev) => {
      if (prev.includes(name)) return prev.filter((p) => p !== name);
      if (prev.length >= 2) return prev;
      return [...prev, name];
    });
  }

  async function predictFight() {
    if (selected.length !== 2) return;

    let fighter1name = selected[0];
    let fighter2name = selected[1];

    setLoading(true);
    setPrediction(null);

    try {
      const res = await fetch("../api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fighter1: fighter1name,
          fighter2: fighter2name,
        }),
      });

      const data = await res.json();
      setPrediction(data);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }

  const displayRank = (r: number) => (r === 1 ? "Champ" : `Rank ${r - 1}`);

  return (
    <form className="fighter-picker">
      <table className="fighter-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Record</th>
            <th>Rank</th>
          </tr>
        </thead>
        <tbody>
          {initialList
            .sort((a, b) => a.rating - b.rating)
            .map((fighter) => {
              const checked = selected.includes(fighter.name);
              const disabled = selected.length >= 2 && !checked;
              const isHovered = hovered === fighter.name;
              const isActive = checked || isHovered;
              return (
                <tr
                  key={fighter.name}
                  className={`fighter-row ${checked ? "selected" : ""}`}
                  onClick={() => !disabled && toggle(fighter.name)}
                  onMouseEnter={() => setHovered(fighter.name)}
                  onMouseLeave={() => setHovered(null)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      if (!disabled) toggle(fighter.name);
                    }
                  }}
                >
                  <td className="name-cell">
                    {isActive ? fighter.nickname || fighter.name : fighter.name}
                  </td>
                  <td className="record-cell">{fighter.record}</td>
                  <td className="rank-cell">{displayRank(fighter.rating)}</td>
                </tr>
              );
            })}
        </tbody>
      </table>

      <div className="flex justify-center mt-6">
        <button
          type="button"
          className="px-8 py-3 bg-[#ad2929] text-white rounded-lg text-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed w-full max-w-[500px]"
          disabled={selected.length !== 2}
          onClick={predictFight}
        >
          {loading ? "Predicting..." : "Predict Fight"}
        </button>
      </div>

      <div className="justify-center mt-6">
        {prediction && (
          <div className="mt-6 text-center">
            <h2 className="text-xl font-bold">Prediction</h2>
            <p>
              Winner: <strong>{prediction.winner}</strong>
            </p>
            <p>Probability: {Math.round(prediction.confidence * 100)}%</p>
          </div>
        )}
      </div>

      <style jsx>{`
        .fighter-picker {
          margin-top: 1rem;
        }

        .fighter-table {
          width: 100%;
          max-width: 1100px;
          margin: 0 auto;
          border-collapse: collapse;
          table-layout: fixed; /* forces fixed column widths to prevent layout shift */
        }
        .fighter-table th,
        .fighter-table td {
          border: 1px solid rgba(0, 0, 0, 0.08);
          padding: 8px 12px;
          text-align: left;
          vertical-align: middle;
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .fighter-table thead th {
          background: rgba(17, 17, 17, 0.95);
          color: white;
        }
        /* fixed column widths (sum ~100%) */
        .fighter-table thead th:nth-child(1) {
          width: 55%;
        }
        .fighter-table thead th:nth-child(2) {
          width: 30%;
        }
        .fighter-table thead th:nth-child(3) {
          width: 15%;
          text-align: center;
        }
        .name-cell {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
        }
        .fighter-row {
          cursor: pointer;
          transition: background 0.12s ease, color 0.12s ease,
            box-shadow 0.12s ease;
        }
        .fighter-row:hover,
        .fighter-row.selected {
          background: #ad2929;
          color: white;
        }
        /* add a dark red inset border only when a row is selected (picked) */
        .fighter-row.selected {
          box-shadow: inset 0 0 0 3px #7a0b0b;
        }
        .fighter-row:hover .name-cell,
        .fighter-row.selected .name-cell {
          color: black;
          font-style: italic;
          font-weight: 700;
        }
        .rank-cell {
          color: #ad2929;
          font-weight: 700;
        }
        .fighter-row:hover .rank-cell,
        .fighter-row.selected .rank-cell {
          color: black;
          font-weight: 700;
        }
        .fighter-row:hover .record-cell,
        .fighter-row.selected .record-cell {
          color: black;
          font-weight: 700;
        }
      `}</style>
    </form>
  );
}
