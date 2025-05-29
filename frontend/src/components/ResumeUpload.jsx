import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { UploadCloud } from "lucide-react";
import React, { useRef, useState } from "react";

export default function ResumeUpload({ setResume }) {
  const fileInput = useRef();
  const [fileName, setFileName] = useState("");
  const [uploadStatus, setUploadStatus] = useState(""); // For subtle confirmation

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setFileName(file.name);
    setUploadStatus(""); // Reset status while uploading
    const formData = new FormData();
    formData.append("file", file);
    const API_URL = import.meta.env.VITE_API_URL;
    const res = await fetch(`${API_URL}/upload_resume`, {
    method: "POST",
    body: formData,
    });
    // const res = await fetch("http://localhost:8000/upload_resume", {
    //   method: "POST",
    //   body: formData,
    // });
    const data = await res.json();
    setResume(data.resume);
    setUploadStatus("Resume uploaded and parsed!");
  };

  return (
    <Card className="mb-8 shadow-lg">
      <CardContent className="flex flex-col items-center py-8">
        <UploadCloud className="w-12 h-12 text-indigo-500 mb-2" />
        <h2 className="text-xl font-semibold mb-2">Upload Your Resume (PDF)</h2>
        <input
          type="file"
          accept="application/pdf"
          ref={fileInput}
          onChange={handleUpload}
          className="hidden"
          id="resume-upload"
        />
        <label htmlFor="resume-upload">
          <Button asChild variant="outline" className="mt-2">
            <span>Choose File</span>
          </Button>
        </label>
        {/* Show file name if uploaded */}
        {fileName && (
          <div className="mt-3 text-sm text-gray-700">
            <span className="font-medium">Selected file:</span> {fileName}
          </div>
        )}
        {/* Subtle confirmation line */}
        {uploadStatus && (
          <div className="mt-2 text-green-600 text-sm font-medium">
            {uploadStatus}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
