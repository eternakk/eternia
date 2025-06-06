import React from 'react';
import { useZone } from '../contexts/ZoneContext';

interface ZoneModifiersProps {
  zoneName?: string; // Optional: if not provided, uses the current zone
  className?: string;
}

/**
 * Component to display modifiers for a zone
 * 
 * If zoneName is not provided, it displays modifiers for the current zone.
 */
export const ZoneModifiers: React.FC<ZoneModifiersProps> = ({ 
  zoneName, 
  className = '' 
}) => {
  const { currentZone, getModifiersForZone, zoneModifiers } = useZone();
  
  // Use the provided zoneName or fall back to the current zone
  const targetZone = zoneName || currentZone;
  
  // If no zone is specified or available, show a message
  if (!targetZone) {
    return <div className={`zone-modifiers ${className}`}>No active zone</div>;
  }
  
  // Get modifiers for the target zone
  const modifiers = getModifiersForZone(targetZone);
  
  // If no modifiers, show a message
  if (!modifiers || modifiers.length === 0) {
    return (
      <div className={`zone-modifiers ${className}`}>
        <h3>Zone: {targetZone}</h3>
        <p>No modifiers active</p>
      </div>
    );
  }
  
  return (
    <div className={`zone-modifiers ${className}`}>
      <h3>Zone: {targetZone}</h3>
      <h4>Active Modifiers:</h4>
      <ul className="modifier-list">
        {modifiers.map((modifier, index) => (
          <li key={index} className="modifier-item">
            {modifier}
          </li>
        ))}
      </ul>
    </div>
  );
};

/**
 * Component to display modifiers for all zones
 */
export const AllZoneModifiers: React.FC<{ className?: string }> = ({ 
  className = '' 
}) => {
  const { zoneModifiers } = useZone();
  
  // If no modifiers for any zone, show a message
  if (!zoneModifiers || Object.keys(zoneModifiers).length === 0) {
    return <div className={`all-zone-modifiers ${className}`}>No zone modifiers active</div>;
  }
  
  return (
    <div className={`all-zone-modifiers ${className}`}>
      <h3>All Zone Modifiers</h3>
      {Object.entries(zoneModifiers).map(([zoneName, modifiers]) => (
        <div key={zoneName} className="zone-section">
          <h4>{zoneName}</h4>
          {modifiers.length === 0 ? (
            <p>No modifiers active</p>
          ) : (
            <ul className="modifier-list">
              {modifiers.map((modifier, index) => (
                <li key={index} className="modifier-item">
                  {modifier}
                </li>
              ))}
            </ul>
          )}
        </div>
      ))}
    </div>
  );
};