import React from "react";
import Link from "next/link";
import Image from "next/image";

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="nav-inner">
        <Link href="/" className="nav-logo" aria-label="Home">
          <Image
            src="/images/UFC-01.svg"
            alt="UFC"
            width={40}
            height={40}
            className="logo-img"
          />
          <span className="brand">FIGHT PREDICTION</span>
        </Link>
        <div className="nav-spacer" />
      </div>
    </nav>
  );
}
