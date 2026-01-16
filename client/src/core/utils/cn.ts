/**
 * Utility function for merging Tailwind CSS classes
 *
 * Combines multiple class names and handles conditional classes
 *
 * @example
 * cn('px-4 py-2', isActive && 'bg-blue-500', className)
 */

type ClassValue = string | number | boolean | undefined | null | ClassValue[];

export function cn(...classes: ClassValue[]): string {
  return classes
    .flat()
    .filter((c) => typeof c === 'string' && c.length > 0)
    .join(' ')
    .trim();
}
