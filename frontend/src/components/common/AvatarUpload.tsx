import React, { useRef, useState } from 'react';
import Avatar from './Avatar';
import Button from './Button';

interface AvatarUploadProps {
  username: string;
  userId?: number;
  onAvatarSelected?: (file: File) => void;
  onAvatarUploaded?: () => void;
  selectedFile?: File | null;
  showConfirmButton?: boolean;
  uploadFunction?: (file: File) => Promise<void>;
}

const AvatarUpload: React.FC<AvatarUploadProps> = ({ 
  username, 
  userId, 
  onAvatarSelected, 
  onAvatarUploaded,
  selectedFile, 
  showConfirmButton = false,
  uploadFunction 
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && file.type.startsWith('image/')) {
      onAvatarSelected?.(file);
      
      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleConfirm = async () => {
    if (!selectedFile || !uploadFunction) return;
    
    setIsUploading(true);
    try {
      await uploadFunction(selectedFile);
      setPreview(null);
      onAvatarUploaded?.();
    } catch (error) {
      console.error('Avatar upload failed:', error);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="flex flex-col items-center gap-4">
      <div 
        className="relative cursor-pointer group"
        onClick={() => fileInputRef.current?.click()}
      >
        {preview ? (
          <img
            src={preview}
            alt="Avatar preview"
            className="w-24 h-24 rounded-full object-cover border-2 border-blue-400"
          />
        ) : (
          <Avatar username={username} userId={userId} size="lg" />
        )}
        <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 rounded-full transition-all flex items-center justify-center">
          <span className="text-white opacity-0 group-hover:opacity-100 transition-opacity text-sm font-medium">
            Click to upload
          </span>
        </div>
      </div>
      
      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />
      
      {selectedFile && (
        <>
          <p className="text-sm text-gray-600">{selectedFile.name}</p>
          {showConfirmButton && uploadFunction && (
            <div className="flex gap-2">
              <Button 
                onClick={handleConfirm} 
                loading={isUploading}
                size="sm"
              >
                Confirm Upload
              </Button>
              <Button 
                onClick={() => {
                  setPreview(null);
                  onAvatarSelected?.(null as any);
                  if (fileInputRef.current) fileInputRef.current.value = '';
                }}
                variant="secondary"
                size="sm"
                disabled={isUploading}
              >
                Cancel
              </Button>
            </div>
          )}
        </>
      )}
      
      <p className="text-xs text-gray-500 text-center">
        Click to choose an avatar {!showConfirmButton && '(optional)'}
      </p>
    </div>
  );
};

export default AvatarUpload;
