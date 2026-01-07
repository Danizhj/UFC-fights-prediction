import React from "react";
import FighterPicker from "@/components/FighterPicker";
import fighters from "@/data/fighterdata.json";

export default async function FighterSelection({
  params,
}: {
  params: Promise<{ weightclass: string }>;
}) {
  const { weightclass } = await params;

  const normalize = (s?: string) =>
    (s || "")
      .toString()
      .toLowerCase()
      .replace(/[^a-z0-9]/g, "");
  const wc = normalize(weightclass);
  const list = (fighters as any[]).filter((f) => normalize(f.division) === wc);

  return (
    <main>
      <header className="ufc-header">
        <h1>{weightclass.charAt(0).toUpperCase() + weightclass.slice(1)}</h1>
      </header>

      <section>
        {list.length === 0 ? (
          <p>No fighters found for this division.</p>
        ) : (
          <FighterPicker initialList={list} />
        )}
      </section>
    </main>
  );
}
