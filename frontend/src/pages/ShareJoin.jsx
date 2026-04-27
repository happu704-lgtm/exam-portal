import React, { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Loader2, Link2, AlertCircle } from 'lucide-react'
import API_ENDPOINTS from '../config/api'
import toast from 'react-hot-toast'

export default function ShareJoin() {
  const { token } = useParams()
  const navigate = useNavigate()
  const [isValidating, setIsValidating] = useState(true)
  const [isValid, setIsValid] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    validateAndRedirect()
  }, [token])

  const validateAndRedirect = async () => {
    try {
      setIsValidating(true)
      
      // Call the backend to validate the share token
      const response = await fetch(`${API_ENDPOINTS.SHARE.JOIN}/${token}`, {
        method: 'GET',
        credentials: 'include',
        redirect: 'follow',
      })

      // The backend will redirect to login with session set
      // If we get here, it means we're handling the redirect in frontend
      
      // Store the token in localStorage for post-login redirect
      localStorage.setItem('share_token', token)
      
      // Show welcome message
      toast.success('Welcome! Please login or register to continue.', {
        duration: 5000,
      })
      
      // Redirect to login page
      setIsValid(true)
      setTimeout(() => {
        navigate('/login?redirect=/student')
      }, 2000)
      
    } catch (error) {
      console.error('Share link error:', error)
      setError('Invalid or expired link. Please contact your administrator.')
      setIsValid(false)
      
      // Still redirect to login after showing error
      setTimeout(() => {
        navigate('/login')
      }, 3000)
    } finally {
      setIsValidating(false)
    }
  }

  if (isValidating) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 animate-spin text-blue-600 mx-auto" />
          <h2 className="text-xl font-semibold text-gray-900">
            Validating your link...
          </h2>
          <p className="text-sm text-gray-600">
            Please wait while we verify your access
          </p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-100 px-4">
        <div className="text-center space-y-4 max-w-md">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto">
            <AlertCircle className="w-8 h-8 text-red-600" />
          </div>
          <h2 className="text-xl font-semibold text-gray-900">
            Link Error
          </h2>
          <p className="text-sm text-gray-600">
            {error}
          </p>
          <p className="text-xs text-gray-500">
            Redirecting to login page...
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 to-emerald-100 px-4">
      <div className="text-center space-y-4">
        <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
          <Link2 className="w-8 h-8 text-green-600" />
        </div>
        <h2 className="text-xl font-semibold text-gray-900">
          Link Verified!
        </h2>
        <p className="text-sm text-gray-600">
          Welcome to Digital Quiz Tool. Redirecting to login...
        </p>
      </div>
    </div>
  )
}
