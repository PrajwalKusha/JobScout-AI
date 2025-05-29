import React, { useEffect } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

function getScoreColor(score) {
  if (score >= 0.75) return "bg-green-500";
  if (score >= 0.5) return "bg-yellow-500";
  return "bg-red-500";
}

export default function MatchModal({ open, onClose, job, resume, setMatchResult, matchResult }) {
  useEffect(() => {
    if (open && job && resume) {
      const API_URL = import.meta.env.VITE_API_URL;
      fetch(`${API_URL}/match_job`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(job),
      })
      // fetch("http://localhost:8000/match_job", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify(job),
      // })
        .then((res) => res.json())
        .then((data) => setMatchResult(data));
    }
  }, [open, job, resume, setMatchResult]);

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            {job?.title} @ {job?.company}
          </DialogTitle>
        </DialogHeader>
        {matchResult ? (
          <div>
            <div className="flex items-center gap-4 mb-4">
              <span className="font-semibold">Match Score:</span>
              <div className="flex-1">
                <Progress
                  value={Math.round(matchResult.match_score * 100)}
                  className="h-3"
                  indicatorClassName={getScoreColor(matchResult.match_score)}
                />
              </div>
              <span className={`ml-2 font-bold ${getScoreColor(matchResult.match_score)} text-white px-2 py-1 rounded`}>
                {Math.round(matchResult.match_score * 100)}%
              </span>
            </div>
            <div className="mb-2">
              <span className="font-semibold">Matched Skills:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {matchResult.matched_skills.length > 0 ? (
                  matchResult.matched_skills.map(skill => (
                    <Badge key={skill} variant="success">{skill}</Badge>
                  ))
                ) : (
                  <span className="text-gray-500 text-xs">None</span>
                )}
              </div>
            </div>
            <div className="mb-2">
              <span className="font-semibold">Missing Skills:</span>
              <div className="flex flex-wrap gap-2 mt-1">
                {matchResult.missing_skills.length > 0 ? (
                  matchResult.missing_skills.map(skill => (
                    <Badge key={skill} variant="destructive">{skill}</Badge>
                  ))
                ) : (
                  <span className="text-gray-500 text-xs">None</span>
                )}
              </div>
            </div>
            <div className="mb-2">
              <span className="font-semibold">Suggestions:</span>
              <span className="ml-2">{matchResult.suggestions}</span>
            </div>
            <div className="flex justify-end mt-4">
              <Button onClick={onClose} variant="outline">Close</Button>
            </div>
          </div>
        ) : (
          <div>Loading match...</div>
        )}
      </DialogContent>
    </Dialog>
  );
}
