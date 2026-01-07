import GenderSwitch from "../components/CardSelection";

const page = () => {
  return (
    <main className="ufc-hero">
      <header className="ufc-header">
        <h1>Pick a Weight Class</h1>
        <p className="lead">
          Choose the weight division where you'll pick fighters.
        </p>
      </header>

      <GenderSwitch />
    </main>
  );
};

export default page;
