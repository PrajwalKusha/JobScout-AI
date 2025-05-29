import { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import React, { useState } from "react";
import { Combobox } from './ComboBox';

const roles = [
  "Data Analyst",
  "Business Analyst",
  "Machine Learning Engineer",
  "Solutions Architect",
  "Data Engineer",
  "Data Scientist"
];
const locations = [
  "Washington, DC",
  "New York",
  "Arlington"
];

const frequencies = Array.from({ length: 10 }, (_, i) => ({
  value: (i + 1).toString(),
  label: (i + 1).toString(),
}));

export default function JobSearch({ setJobs, setLoadingJobs }) {
  const [role, setRole] = useState("");
  const [location, setLocation] = useState("");
  const [frequency, setFrequency] = React.useState("5");

  const handleSearch = async (e) => {
    e.preventDefault();
    setLoadingJobs(true);
    const formData = new FormData();
    formData.append("role", role);
    formData.append("location", location);
    formData.append("frequency", frequency);
    const res = await fetch("http://localhost:8000/scrape_jobs", {
      method: "POST",
      body: formData,
    });
    const data = await res.json();
    setJobs(data.jobs);
    setLoadingJobs(false);
  };

  return (
    <form onSubmit={handleSearch} className="mb-8 flex flex-col md:flex-row gap-4 items-end">
      <div>
        <label className="block text-sm font-medium mb-1">Role</label>
        <Combobox
          options={roles}
          value={role}
          onChange={setRole}
          placeholder="Select a role"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Location</label>
        <Combobox
          options={locations}
          value={location}
          onChange={setLocation}
          placeholder="Select a location"
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Number of Jobs</label>
        <Combobox
          options={frequencies}
          value={frequency}
          onChange={setFrequency}
          placeholder="Select number"
        />
      </div>
      <Button type="submit" className="h-10 px-6 bg-blue-700 text-white font-semibold rounded shadow hover:bg-blue-800">
        Search Jobs
      </Button>
    </form>
  );
}
