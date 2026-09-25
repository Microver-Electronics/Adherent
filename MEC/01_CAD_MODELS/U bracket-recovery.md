# U bracket CAD recovery

The local `U bracket.SLDPRT` is only a Git LFS pointer, not the CAD model.
The original repository returned HTTP 404 for its object during migration.
The pointer remains local and ignored so it does not prevent GitHub pushes.

Original object SHA-256: `521714e37d3652d6d5e93c6112689d84c9054d6c8f65e505774f4a12ce420c95`

Expected size: 176036 bytes.

Restore the actual model from a backup or its author, remove its `.gitignore`
entry, and commit the recovered file.
