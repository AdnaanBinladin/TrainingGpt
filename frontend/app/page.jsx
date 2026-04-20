"use client";

import { useState } from "react";

import ChatSection from "../components/ChatSection";
import UploadSection from "../components/UploadSection";

const TEAMS = ["cloud", "dayforce"];

export default function Page() {
  const [team, setTeam] = useState("cloud");

  return (
    <main className="page">
      <h1>RAG Test UI</h1>

      <section className="box">
        <h2>Team Selection</h2>
        <label htmlFor="team-select">Active Team</label>
        <select id="team-select" value={team} onChange={(event) => setTeam(event.target.value)}>
          {TEAMS.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </section>

      <UploadSection team={team} />
      <ChatSection team={team} />
    </main>
  );
}
