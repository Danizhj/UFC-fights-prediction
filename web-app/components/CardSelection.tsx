"use client";

import React from "react";
import Link from "next/link";
import Image from "next/image";

const weightClasses = [
  { name: "Flyweight", img: "/images/flyweight-image.jpg", gender: "male" },
  {
    name: "Bantamweight",
    img: "/images/bantamweight-image.jpg",
    gender: "male",
  },
  {
    name: "Featherweight",
    img: "/images/featherweight-image.jpg",
    gender: "male",
  },
  { name: "Lightweight", img: "/images/lightweight-image.jpg", gender: "male" },
  {
    name: "Welterweight",
    img: "/images/welterweight-image.jpg",
    gender: "male",
  },
  {
    name: "Middleweight",
    img: "/images/middleweight-image.jpg",
    gender: "male",
  },
  {
    name: "Light Heavyweight",
    img: "/images/lightheavyweight-image.jpg",
    gender: "male",
  },
  { name: "Heavyweight", img: "/images/heavyweight-image.jpg", gender: "male" },
  {
    name: "Strawweight (Women)",
    img: "/images/woman-strawweight-image.jpg",
    gender: "female",
  },
  {
    name: "Flyweight (Women)",
    img: "/images/woman-flyweight-image.jpg",
    gender: "female",
  },
  {
    name: "Bantamweight (Women)",
    img: "/images/woman-bantamweight-image.jpg",
    gender: "female",
  },
  {
    name: "Featherweight (Women)",
    img: "/images/woman-featherweight-image.jpg",
    gender: "female",
  },
];

export default function CardSelection({
  initialGender = "male",
}: {
  initialGender?: "male" | "female";
}) {
  const [gender, setGender] = React.useState<"male" | "female">(initialGender);

  const filtered = weightClasses.filter((w) => w.gender === gender);

  return (
    <>
      <div className="mt-6 flex items-center justify-center">
        <div className="inline-flex rounded-full bg-white/10 p-1">
          <button
            aria-pressed={gender === "male"}
            className={`px-4 py-2 rounded-full transition-colors text-sm font-medium ${
              gender === "male" ? "bg-white text-black shadow" : "text-white/80"
            }`}
            onClick={() => setGender("male")}
          >
            Male
          </button>
          <button
            aria-pressed={gender === "female"}
            className={`px-4 py-2 rounded-full transition-colors text-sm font-medium ${
              gender === "female"
                ? "bg-white text-black shadow"
                : "text-white/80"
            }`}
            onClick={() => setGender("female")}
          >
            Female
          </button>
        </div>
      </div>

      <section className="weight-grid mt-6" aria-label="Weight classes">
        {filtered.map((wc) => {
          const slug = wc.name
            .toLowerCase()
            .replace(/\s+/g, "-")
            .replace(/[^a-z0-9-]/g, "");
          return (
            <article key={wc.name} className="weight-card">
              <div className="card-media relative h-[330px] overflow-hidden">
                <Image
                  src={wc.img}
                  alt={wc.name}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="card-body">
                <h3>{wc.name}</h3>
              </div>
              <div className="card-actions">
                <Link href={`/${slug}`} className="select-btn">
                  Select
                </Link>
              </div>
            </article>
          );
        })}
      </section>
    </>
  );
}
