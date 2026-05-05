import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = '' }) => (
  <div className={`animate-pulse bg-slate-100 rounded-2xl ${className} transition-colors duration-300`} />
);

export const CardSkeleton: React.FC = () => (
  <div className="premium-card overflow-hidden h-full flex flex-col bg-white border border-slate-100 transition-colors duration-300">
    {/* Image Skeleton */}
    <Skeleton className="aspect-[16/10] w-full rounded-none" />
    
    <div className="p-6 flex-1 flex flex-col space-y-6">
      <div className="space-y-3">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>

      <div className="grid grid-cols-2 gap-4 pb-2">
        <Skeleton className="h-3 w-3/4" />
        <Skeleton className="h-3 w-3/4" />
      </div>

      <div className="pt-6 border-t border-slate-100 flex justify-between items-end mt-auto transition-colors">
        <div className="space-y-2">
          <Skeleton className="h-2 w-16" />
          <Skeleton className="h-6 w-24" />
        </div>
        <Skeleton className="w-12 h-12 rounded-xl" />
      </div>
    </div>
  </div>
);
