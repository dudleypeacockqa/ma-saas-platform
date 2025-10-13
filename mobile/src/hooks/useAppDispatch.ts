import { useDispatch } from 'react-redux';\n\nimport type { AppDispatch } from '@store/index';\n\nexport const useAppDispatch = () => useDispatch<AppDispatch>();\n
