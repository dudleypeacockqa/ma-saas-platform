import React from 'react';
import { AlertCircle } from 'lucide-react';

// Safe icon wrapper that provides fallbacks for missing icons
const IconSafeWrapper = ({
  icon: Icon,
  fallback: Fallback = AlertCircle,
  className = '',
  size = 16,
  ...props
}) => {
  // If no icon is provided, use fallback
  if (!Icon) {
    return <Fallback className={className} size={size} {...props} />;
  }

  // Try to render the icon, catch any errors
  try {
    return <Icon className={className} size={size} {...props} />;
  } catch (error) {
    console.warn('Failed to render icon:', error);
    return <Fallback className={className} size={size} {...props} />;
  }
};

// Hook to safely import lucide icons
export const useSafeIcon = (iconName) => {
  const [icon, setIcon] = React.useState(null);
  const [error, setError] = React.useState(null);

  React.useEffect(() => {
    const loadIcon = async () => {
      try {
        const lucideModule = await import('lucide-react');
        const IconComponent = lucideModule[iconName];

        if (IconComponent) {
          setIcon(() => IconComponent);
        } else {
          console.warn(`Icon "${iconName}" not found in lucide-react`);
          setError(`Icon "${iconName}" not found`);
        }
      } catch (err) {
        console.error(`Failed to load icon "${iconName}":`, err);
        setError(err.message);
      }
    };

    if (iconName) {
      loadIcon();
    }
  }, [iconName]);

  return { icon, error, isLoading: !icon && !error };
};

// Safe import function for icons
export const safeImportIcon = async (iconName, fallbackIcon = 'AlertCircle') => {
  try {
    const lucideModule = await import('lucide-react');
    return lucideModule[iconName] || lucideModule[fallbackIcon] || lucideModule.AlertCircle;
  } catch (error) {
    console.error(`Failed to import icon "${iconName}":`, error);
    // Return a simple div as ultimate fallback
    return ({ className, ...props }) => (
      <div
        className={`inline-block w-4 h-4 bg-gray-400 rounded ${className}`}
        title={`Icon "${iconName}" failed to load`}
        {...props}
      />
    );
  }
};

// Enhanced icon component with built-in error handling
export const SafeIcon = ({ name, fallback, className, size, ...props }) => {
  const { icon, error, isLoading } = useSafeIcon(name);

  if (isLoading) {
    return (
      <div
        className={`inline-block animate-pulse bg-gray-200 rounded ${className}`}
        style={{ width: size || 16, height: size || 16 }}
      />
    );
  }

  if (error || !icon) {
    const FallbackIcon = fallback || AlertCircle;
    return <FallbackIcon className={className} size={size} {...props} />;
  }

  return <IconSafeWrapper icon={icon} className={className} size={size} {...props} />;
};

export default IconSafeWrapper;