import { FaLinkedin, FaGlobe } from "react-icons/fa";

export default function Footer() {
  return (
    <footer className="w-full mt-12 py-6 bg-white/80 border-t flex flex-col items-center gap-2">
      <p className="text-gray-700 text-sm font-medium">
        Dreamed, designed, and deployed by <span className="font-semibold text-indigo-700">Prajwal Kusha</span>.
      </p>
      <div className="flex gap-4 mt-1">
        <a
          href="https://prajwalkusha.vercel.app"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-indigo-600 hover:underline"
        >
          <FaGlobe className="inline-block" /> Website
        </a>
        <a
          href="https://www.linkedin.com/in/prajwal-kusha"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-indigo-600 hover:underline"
        >
          <FaLinkedin className="inline-block" /> LinkedIn
        </a>
      </div>
    </footer>
  );
}
