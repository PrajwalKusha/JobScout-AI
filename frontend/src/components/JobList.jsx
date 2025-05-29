import React, { useState } from "react";
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function JobList({ jobs, loading, onCheckFit }) {
  const [expandedIdx, setExpandedIdx] = useState(null);

  if (loading) {
    return <div className="text-blue-600">Loading jobs...</div>;
  }
  if (!jobs || jobs.length === 0) {
    return <div className="text-gray-500">No jobs found. Try searching!</div>;
  }
  return (
    <div className="grid gap-4">
      {jobs.map((job, idx) => (
        <Card key={idx} className={`transition-all duration-200 ${expandedIdx === idx ? "ring-2 ring-blue-400" : ""}`}>
          <CardHeader>
            <CardTitle className="text-xl">{job.title}</CardTitle>
            <div className="text-gray-600">{job.company} — {job.location}</div>
            {job.salary && (
              <div className="text-gray-500 text-sm mt-1">{job.salary}</div>
            )}
          </CardHeader>
          <CardContent>
            <div className={`mt-2 text-gray-700 ${expandedIdx === idx ? "" : "line-clamp-2"}`}>
              {job.full_description}
            </div>
            <div className="flex justify-between items-center mt-2">
              <a
                href={job.link}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:underline text-sm"
              >
                View on Indeed
              </a>
              <Button
                variant="ghost"
                onClick={() => setExpandedIdx(expandedIdx === idx ? null : idx)}
              >
                {expandedIdx === idx ? "Show Less ▲" : "Show More ▼"}
              </Button>
            </div>
            {expandedIdx === idx && (
              <div className="mt-4 space-y-2">
                {job.date_posted && (
                  <div>
                    <span className="font-semibold">Date Posted:</span>{" "}
                    <span>{job.date_posted}</span>
                  </div>
                )}
                {job.type && (
                  <div>
                    <span className="font-semibold">Type:</span>{" "}
                    <span>{job.type}</span>
                  </div>
                )}
                {/* Add more job fields here if available */}
              </div>
            )}
          </CardContent>
          <CardFooter className="flex justify-end">
            <Button onClick={() => onCheckFit(job)} className="bg-green-600 hover:bg-green-700">
              Check Resume Fit
            </Button>
          </CardFooter>
        </Card>
      ))}
    </div>
  );
}

