import { TypedUseSelectorHook, useSelector } from 'react-redux';\n\nimport type { RootState } from '@store/index';\n\nexport const useAppSelector: TypedUseSelectorHook<RootState> = useSelector;\n
