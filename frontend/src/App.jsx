import React, { useState } from "react";
import ResumeUpload from "./components/ResumeUpload";
import JobSearch from "./components/JobSearch";
import JobList from "./components/JobList";
import MatchModal from "./components/MatchModal";
import ExportControls from "./components/ExportControls";
import { Card, CardContent } from "@/components/ui/card";
import Footer from "./components/Footer";

function App() {
  const [resume, setResume] = useState(null);
  const [jobs, setJobs] = useState([]);
  const [selectedJob, setSelectedJob] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(false);

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-100 via-white to-blue-200">
      <div className="max-w-3xl mx-auto py-10 px-4">
        <h1 className="text-5xl font-extrabold text-center text-indigo-700 drop-shadow mb-2">JobScout AI</h1>
        <p className="text-center text-lg text-gray-600 mb-8 font-medium tracking-wide">
          Smarter Job Hunting Starts Here
        </p>
        <Card className="mb-6 bg-white/80 border-0 shadow-md">
          <CardContent className="py-4 px-6 text-center">
            <p className="text-base md:text-lg text-gray-700 font-small">
              Upload your resume, search real-time jobs, and instantly see how well you match.<br />
              <span className="text-gray-500 text-sm md:text-base block mt-2">
                JobScout uses <span className="font-semibold text-indigo-600">AI</span> to compare your skills with job listings, giving you a match score, highlighting missing skills, and offering tips to improve your resume — all in one sleek, interactive dashboard.
              </span>
            </p>
          </CardContent>
        </Card>
        <ResumeUpload setResume={setResume} />
        <JobSearch setJobs={setJobs} setLoadingJobs={setLoadingJobs} />
        <JobList
          jobs={jobs}
          loading={loadingJobs}
          onCheckFit={(job) => {
            setSelectedJob(job);
            setShowModal(true);
          }}
        />
        {jobs.length > 0 && (
          <ExportControls jobs={jobs} />
        )}
        <MatchModal
          open={showModal}
          onClose={() => setShowModal(false)}
          job={selectedJob}
          resume={resume}
          setMatchResult={setMatchResult}
          matchResult={matchResult}
        />
        <Footer />
      </div>
    </div>
  );
}

export default App;
