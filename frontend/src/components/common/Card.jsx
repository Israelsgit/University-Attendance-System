import React from "react";
import { cn } from "../../utils/cn";

const Card = ({ children, className, ...props }) => {
  return (
    <div
      className={cn(
        "bg-white/10 backdrop-blur-xl border border-white/20 rounded-lg shadow-lg",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

export default Card;
