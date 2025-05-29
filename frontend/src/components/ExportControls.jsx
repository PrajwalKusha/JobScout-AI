import React, { useState } from "react";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";

function convertJobsToCSV(jobs) {
  if (!jobs.length) return "";
  const headers = Object.keys(jobs[0]);
  const rows = jobs.map(job => headers.map(h => `"${(job[h] || "").toString().replace(/"/g, '""')}"`).join(","));
  return [headers.join(","), ...rows].join("\n");
}

export default function ExportControls({ jobs }) {
  const [open, setOpen] = useState(false);
  const [email, setEmail] = useState("");
  const [sending, setSending] = useState(false);
  const [sent, setSent] = useState(false);

  const handleDownload = () => {
    const csv = convertJobsToCSV(jobs);
    const blob = new Blob([csv], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "jobscout_jobs.csv";
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleSendEmail = async () => {
    setSending(true);
    try {
      const API_URL = import.meta.env.VITE_API_URL;
      const res = await fetch(`${API_URL}/send_jobs_email`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, jobs }),
      });
      // const res = await fetch("http://localhost:8000/send_jobs_email", {
      //   method: "POST",
      //   headers: { "Content-Type": "application/json" },
      //   body: JSON.stringify({ email, jobs }),
      // });
      if (res.ok) setSent(true);
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="flex flex-col md:flex-row gap-4 justify-center mt-8">
      <Button onClick={handleDownload} variant="outline">
        Download .csv
      </Button>
      <Button onClick={() => setOpen(true)} variant="outline">
        Send by Email
      </Button>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Send Jobs by Email</DialogTitle>
          </DialogHeader>
          {sent ? (
            <div className="text-green-600 text-center py-4">Email sent successfully!</div>
          ) : (
            <>
              <Input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="mb-4"
                required
              />
              <DialogFooter>
                <Button onClick={handleSendEmail} disabled={sending || !email}>
                  {sending ? "Sending..." : "Send"}
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
